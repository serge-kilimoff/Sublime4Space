#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOC
"""
from __future__ import unicode_literals, print_function, division
import re
from indent_tokens import RootToken, TextToken

__author__ = "Serge Kilimoff-Goriatchkine"
__email__ = "serge.kilimoff@gmail.com"



def scanner_from(language, lexicon_variant=None, grammar_variant=None):
    module_name = 'lexicon.%s_tokens' % language.lower()

    if lexicon_variant:
        lexicon_name = '%s_%s_LEXICON' % (language.upper(), lexicon_variant.upper())
    else:
        lexicon_name = '%s_LEXICON' % language.upper()

    if grammar_variant:
        grammar_name = '%s_%s_GRAMMAR' % (language.upper(), grammar_variant.upper())
    else:
        grammar_name = '%s_GRAMMAR' % language.upper()

    module = __import__(module_name, fromlist=[lexicon_name, grammar_name])
    lexicon = getattr(module, lexicon_name)
    grammar_rules = getattr(module, grammar_name, None)
    return Scanner(lexicon, grammar_rules=grammar_rules)



class Scanner(object):
    def __init__(self, lexicon, text_node=TextToken, grammar_rules=None, re_flags=None):
        """
        Tokenise et réindente un code.

        PARAMETERS
        ==========
        lexicon : dict
            Les clés de ce dictionnaire sont des expressions régulières non compilés, et les valeurs des fonctions qui retourneront
            des instances de tokens.

        [text_node : Token]
            Le token qui représentera tout ce qui n'apppartient pas aux tokens définis dans le lexicon.

        [grammar_rules : dict]
            Les clés de ce dictionnaire sont des classes Token, définis dans le lexicon. Les valeurs sont des fonctions.
            Une nouvelle classe sera crée à partir de la clé, et sa fonction __unicode__ sera surchargé à partir de la fonction défini en valeur.
            Voir `Scanner.subclassing_from_grammar`.

        [re_flags : int]
            Les drapeaux définis dans le module re, qui seront utilisés pour compiler la regex de tokenisation.

        RAISES
        ======
        ValueError : Si les clés/valeurs de lexicon ne correspondent pas à ce qui est indiqué dans la description de `lexicon`
        """
        if not grammar_rules:
            grammar_rules = dict()
        self.tokenizers = dict()
        pattern = ""

        for index, item in enumerate(lexicon.iteritems()):
            regex, tokenizer = item
            if not isinstance(regex, unicode):
                raise ValueError("regex in lexicon need to be an unicode string, get %r. (key=%r" % (type(regex), regex))
            if not callable(tokenizer):
                raise ValueError("tokenizer in lexicon need to be a callable. (key=%r)" % regex)
            uid_tokenizer = "token_%i" % index
            pattern += "|(?P<%s>%s)" % (uid_tokenizer, regex)
            grammar_rule = grammar_rules.get(tokenizer, None)
            if grammar_rule:
                tokenizer = self.subclassing_from_grammar(tokenizer, grammar_rule)
            self.tokenizers[uid_tokenizer] = tokenizer

        self.lexicon = re.compile(pattern.strip('|'), *(re_flags or list()))
        text_grammar_rule = grammar_rules.get(text_node, None)
        if text_grammar_rule:
            text_node = self.subclassing_from_grammar(text_node, text_grammar_rule)
        self.text_node = text_node


    def subclassing_from_grammar(self, cls, grammar_rule):
        """
        Crée dynamiquement une nouvelle classe par héritage de la classe `cls`.
        Sa propriété __unicode__ sera surchargé par `grammar_rule`.

        PARAMETERS
        ==========
        cls : Token
            Une classe ayant les propriétés de la classe `Token`.

        grammar_rule : callable
            Une fonction. Elle devra avoir en argument le mot clé `self` car elle sera une méthode d'instance.
        """
        cls_name = '%s__with_rule_%s' % (cls.__name__, grammar_rule.__name__)
        cls_dict = dict(**cls.__dict__)
        cls_dict['__unicode__'] = grammar_rule
        return type(cls_name.encode('utf-8'), (cls,), cls_dict)


    def parse(self, string):
        """
        Tokenise `string`. Cette tokenisation prendra la forme d'une liste simple de Token.
        La tokenisation utilise l'attribut lexicon de ce scanner. Chaque partie de la string ne matchant pas avec
        une clé de ce lexicon sera tokenisé en TextToken.

        PARAMETERS
        ==========
        string : unicode
            La chaine à tokeniser.

        RETURNS
        =======
        list : Une liste de Token.
        """
        tokens = list()

        while True:
            if not string:
                break
            matchobj = self.lexicon.search(string)
            if not matchobj:
                tokens.append(self.text_node(string))
                break

            prestring = string[:matchobj.start()]
            if prestring:
                tokens.append(self.text_node(prestring))

            tokenizer = self.tokenizers[matchobj.lastgroup]
            tokens.append(tokenizer(matchobj))
            string = string[matchobj.end():]

        return tokens


    def construct_tree(self, tokens):
        """
        À partir d'une liste de tokens, construit un arbre hiérarchique de ces tokens.
        Chaque Token se verra attribuer un attribut `preceding` et `following` correspondant
        au Token précédant/suivant dans la liste `tokens`.

        PARAMETERS
        ==========
        tokens : list
            La liste de tokens à hiérarchiser.

        RETURNS
        =======
        Token : Le token racine, qui contiendra tout les autres tokens.
        """
        root = RootToken()
        node = previous_token = root

        for token in tokens:
            token.preceding = previous_token
            previous_token.following = token
            node = node.hierarchise(token)
            previous_token = token
        return root


    def serialize(self, token, strings=None):
        if not strings:
            strings = list()
        self._serialize(token, strings)
        return ''.join(strings)

    def _serialize(self, token, strings):
        strings.append(unicode(token))
        for child in token.children:
            self._serialize(child, strings)

    def serialize2(self, token, indentation=None):
        """
        Transforme `token` et les Token qui le suivent dans la chaine en une chaine de caractère.

        PARAMETERS
        ==========
        token : Token
            Le token où débuté la sérialisation.

        RETURNS
        =======
        str : La chaine de caractère représentant la chaine de Tokens.
        """
        strings = list()
        while True:
            if not token:
                break
            if indentation:
                token.indentation = indentation
            strings.append(unicode(token))
            token = token.following
        return "".join(strings)


    def indent(self, string, indentation=None):
        """
        Réindente `string` suivant le lexicon et les règles grammaticales fournis
        à l'instanciation de la classe `Scanner`.

        PARAMETERS
        ==========
        string : unicode
            Le code à indenter

        RETURNS
        =======
        unicode : le code (normalement) indenté
        """
        tokens = self.parse(string)
        root = self.construct_tree(tokens)
        return self.serialize2(root, indentation)
