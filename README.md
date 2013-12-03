Sublime4Space
=============

Parse, tokenize et réindente un code source. Version beta, l'explication qui suit sera revu et complété.


Comment l'utiliser
------------------
```python
>>> from scanner import scanner_from
>>> xml = "<body><section1><title>Foo<em>Title</title>Bar</em></section1></body>"
>>> scanner = scanner_from('xml')
>>> result = scanner.indent(xml, indentation='****')
>>> print(result)

<body>
****<section1>
********<title>Foo<em>Title</title>Bar</em>
****</section1>
</body>

>>> scanner = scanner_from('css')
>>> css = "body{display:block;}\n\nsection1{margin:auto;}"
>>> result = scanner.indent(css, indentation="    ")
>>> print(result)

body
{
    display:block;
}

section1
{
    margin:auto;
}
```


Quels langages sont supportés ?
-------------------------------
Pour le moment, seul xml et css, en version prototype. Dans une avenir proche : css, xml, html, php, js et un mélange de tout ces langages.



Pourquoi ce programme ?
-----------------------
Pour réindenter du code "sale". Il existe une multitude de programme qui permettent de réindenter, par exemple, du xml. Mais il y en a peu qui permettent de réindenter du code xml invalide, sans modifier le code. De plus, il garde les retours à la ligne initiaux.
Et il me faut aussi un code qui permettent de rajouter et de mixer rapidement le support d'autres langages.
Ce programme n'a pas pour but de valider un quelconque code, ou de se substituer à un tokeniser plus avancé comme pyparser, ce n'est pas son but. Gardons les choses simples et stupide !
De plus, cela facilite le debug pour, par exemple, une validation DTD d'un xml. Il est toujours un peu fastidieux de rechercher la position d'un caractère plutôt que le numéro d'une ligne, dans le cas d'un xml inline.



Comment ajouter le support d'un nouveau langage ?
-------------------------------------------------
En définissant dans un premier temps les regex qui permettront de tokeniser le code. Puis de définir, si besoin, les règles de grammaire qui lieront ces tokens. Ces règles de grammaire sont uniquement là pour définir les indentations, rien d'autres.
Exemple avec le xml :
```python
# Définit les règles de tokenisation du xml. Les regexp sont associés à des classes de token.
# Pour le moment, ce sont des regexp basiques.
XML_LEXICON = {
    r"\s*\n+\s*" : WhitespaceToken,
    r"<[^/!][^>]*[^/]?>" : OpenToken,
    r"</[^>]*[^/]>" : CloseToken,
    r"<[^/!][^>]*/>" : InlineToken,
    r"<!--.*?-->" : BlockToken,
    r"<\?.*?\?>" : BlockToken,
    r"<!DOCTYPE.*?>" : BlockToken,
}

# Définit les règles de grammaire.
# Chaque classe de token lié plus haut est associé à une fonction qui permettra son indentation.
# Si une règle de grammaire retourne None, alors la fonction __unicode__ de la classe parente est
# automatiquement appelé.
def serialize_open_tag(token):
    if isinstance(token.preceding, TextToken):
        return token.data


def serialize_close_tag(token):
    if isinstance(token.preceding, OpenToken):
        return token.data
    if isinstance(token.preceding, TextToken):
        return token.data


def serialize_text(token):
    if isinstance(token.preceding, (OpenToken, CloseToken)):
        return token.data



XML_GRAMMAR = {
    OpenToken : serialize_open_tag,
    CloseToken : serialize_close_tag,
    TextToken : serialize_text,
}
```
