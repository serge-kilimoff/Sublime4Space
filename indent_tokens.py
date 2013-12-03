#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Les tokens de base utilisés pour indenter un code.
"""
from __future__ import unicode_literals, print_function, division


__author__ = "Serge Kilimoff-Goriatchkine"
__email__ = "serge.kilimoff@gmail.com"
__license__ = 'MIT license'



class Token(object):
    """ Classe 'abstraite' pour les tokens """
    def __init__(self, data):
        """
        PARAMETERS
        ==========
        data : all
            Les données à enregistrer dans le token.
        """
        self.children = list()
        self.parent = None
        self.data = data
        self._preceding = None
        self.following = None
        self._indentation = ''


    @property
    def preceding(self):
        """
        Retourne le token précédent dans l'arbre, en sautant les WhitespaceToken.
        À comprendre comme un preceding en XPath, et non comme un preceding-sibling. C'est à dire
        que le premier token inclus dans un autre token aura comme token.preceding == token.parent
        et non token.preceding == None.
        """
        token = self._preceding
        while True:
            if not isinstance(token, WhitespaceToken):
                break
            token = token._preceding
        return token

    @preceding.setter
    def preceding(self, token):
        """
        Définit le token suivant dans l'arbre.

        PARAMETERS
        ==========
        token : Token
            Le token qui suivra celui-ci.
        """
        self._preceding = token

    @property
    def depth(self):
        """
        Retourne la profondeur du token dans l'arborescence.
        /!\ Pour des raisons de performances, cet attribut n'est pas recalculé à chaque fois.
        Il ne l'est que la première fois qu'on y accède. Pour recharger la profondeur, cela nécéssite
        un del token._depth, qui est la valeur en cache.
        """
        if not getattr(self, '_depth', None):
            self._depth = self.parent.depth + 1
        return self._depth

    @property
    def indentation(self):
        return self._indentation * self.depth

    @indentation.setter
    def indentation(self, indent):
        self._indentation = indent

    # @abc.abstractmethod
    def hierarchise(self, token):
        """
        Hiérarchise le noeud passé en paramètre par rapport au noeud courrant.
        Cette classe 'abstraite' ne définit pas d'implémentation. Voir les classes hérités.

        PARAMETERS
        ==========
        token : Token
            Le token à hiérarchiser

        RETURNS
        =======
        Token : Le noeud qui sera la racine pour le prochain élement à hiérarchiser
        """
        raise NotImplementedError()

    def __unicode__(self):
        return "\n%s%s" % (self.indentation, self.data)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __repr__(self):
        return "<{} data={!r}>".format(self.__class__.__name__, self.data[:10])



class RootToken(Token):
    def __init__(self):
        Token.__init__(self, '')

    @property
    def depth(self):
        return -1

    def hierarchise(self, token):
        self.children.append(token)
        token.parent = self
        if isinstance(token, OpenToken):
            return token
        return self

    def __unicode__(self):
        return ""



class TokenFromRegex(Token):
    def __init__(self, matchobj):
        Token.__init__(self, matchobj.group())



class OpenToken(TokenFromRegex):
    def hierarchise(self, token):
        if isinstance(token, CloseToken):
            token.parent = self.parent
            self.parent.children.append(token)
            return self.parent
        token.parent = self
        self.children.append(token)
        if isinstance(token, OpenToken):
            return token
        return self


class BlockToken(TokenFromRegex):
    def hierarchise(self, token):
        return self.parent.hierarchise(token)



class CloseToken(BlockToken):
    pass



class InlineToken(BlockToken):
    def __unicode__(self):
        return self.data



class WhitespaceToken(BlockToken):
    def __unicode__(self):
        breaklines = '\n' * (self.data.count("\n") - 1)
        return breaklines + self.indentation



class TextToken(Token):
    def hierarchise(self, token):
        self.preceding.hierarchise(token)



def subclassing_from_grammar(cls, grammar_rule):
    """
    Crée dynamiquement une nouvelle classe par héritage de la classe `cls`.
    Sa propriété __unicode__ sera surchargé par `wrap__unicode__`, qui appelera `grammar_rule`.
    Si `grammar_rule` retourne None, alors la fonction `__unicode__` de la classe parente sera appelé.

    PARAMETERS
    ==========
    cls : Token
        Une classe ayant les propriétés de la classe `Token`.

    grammar_rule : callable
        Une fonction. Elle devra avoir en argument le mot clé `self` car elle sera une méthode d'instance.
    """
    def wrap__unicode__(token):
        result = grammar_rule(token)
        if result is None:
            return super(token.__class__, token).__unicode__()
        return result
    cls_name = '%s__with_rule_%s' % (cls.__name__, grammar_rule.__name__)
    cls_dict = dict(**cls.__dict__)
    cls_dict['__unicode__'] = wrap__unicode__
    print(wrap__unicode__)
    return type(cls_name.encode('utf-8'), (cls,), cls_dict)
