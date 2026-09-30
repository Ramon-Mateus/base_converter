"""Conversões e operações entre bases 2 e 40 sem base 10 como ponte.

Números grandes são listas de dígitos na base do resultado. Inteiros nativos
representam somente um dígito, uma base ou um transporte local do algoritmo.
"""

from dataclasses import dataclass


ALFABETO = "0123456789abcdefghijklmnopqrstuvwxyz@#$%"
PRECISAO_FRACIONARIA = 10
_VALORES = {simbolo: valor for valor, simbolo in enumerate(ALFABETO)}


class ErroConversao(ValueError):
    """Indica uma base ou representação numérica inválida."""


@dataclass(frozen=True)
class Resultado:
    texto: str
    truncado: bool


@dataclass(frozen=True)
class _Fracao:
    sinal: int
    numerador: list[int]
    denominador: list[int]


def _normalizar(digitos: list[int]) -> list[int]:
    indice = 0
    while indice < len(digitos) - 1 and digitos[indice] == 0:
        indice += 1
    return digitos[indice:]


def _zero(digitos: list[int]) -> bool:
    return len(digitos) == 1 and digitos[0] == 0


def _comparar(a: list[int], b: list[int]) -> int:
    a = _normalizar(a)
    b = _normalizar(b)
    if len(a) != len(b):
        return 1 if len(a) > len(b) else -1
    for digito_a, digito_b in zip(a, b):
        if digito_a != digito_b:
            return 1 if digito_a > digito_b else -1
    return 0


def _somar_listas_de_digitos(a: list[int], b: list[int], base: int) -> list[int]:
    """Soma dois números representados por listas na mesma base."""
    i, j, transporte = len(a) - 1, len(b) - 1, 0
    resultado: list[int] = []
    while i >= 0 or j >= 0 or transporte:
        total = transporte
        if i >= 0:
            total += a[i]
            i -= 1
        if j >= 0:
            total += b[j]
            j -= 1
        resultado.append(total % base)
        transporte = total // base
    resultado.reverse()
    return _normalizar(resultado)


def _subtrair_grandes(a: list[int], b: list[int], base: int) -> list[int]:
    """Calcula a - b; a deve ser maior ou igual a b."""
    resultado = a.copy()
    i, j, emprestimo = len(resultado) - 1, len(b) - 1, 0
    while i >= 0:
        valor = resultado[i] - emprestimo
        if j >= 0:
            valor -= b[j]
            j -= 1
        if valor < 0:
            valor += base
            emprestimo = 1
        else:
            emprestimo = 0
        resultado[i] = valor
        i -= 1
    return _normalizar(resultado)


def _multiplicar_lista_por_fator(
    digitos: list[int], multiplicador: int, base: int
) -> list[int]:
    """Multiplica a lista por um fator pequeno, como um dígito ou uma base."""
    if multiplicador == 0 or _zero(digitos):
        return [0]
    resultado: list[int] = []
    transporte = 0
    for digito in reversed(digitos):
        total = digito * multiplicador + transporte
        resultado.append(total % base)
        transporte = total // base
    while transporte:
        resultado.append(transporte % base)
        transporte //= base
    resultado.reverse()
    return _normalizar(resultado)


def _representar_coeficiente_na_base(valor: int, base: int) -> list[int]:
    """Escreve o valor de um dígito da entrada como lista na base desejada."""
    if valor == 0:
        return [0]
    digitos: list[int] = []
    while valor:
        digitos.append(valor % base)
        valor //= base
    digitos.reverse()
    return digitos


def _somar_coeficiente_na_lista(digitos: list[int], valor: int, base: int) -> list[int]:
    """Representa o coeficiente na base de trabalho e o soma à lista."""
    return _somar_listas_de_digitos(digitos, _representar_coeficiente_na_base(valor, base), base)


def _multiplicar_listas_de_digitos(a: list[int], b: list[int], base: int) -> list[int]:
    """Multiplica dois números representados por listas na mesma base."""
    if _zero(a) or _zero(b):
        return [0]
    resultado = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        transporte = 0
        for j in range(len(b) - 1, -1, -1):
            posicao = i + j + 1
            total = resultado[posicao] + a[i] * b[j] + transporte
            resultado[posicao] = total % base
            transporte = total // base
        resultado[i] += transporte
    return _normalizar(resultado)


def _dividir_grandes(
    dividendo: list[int], divisor: list[int], base: int
) -> tuple[list[int], list[int]]:
    if _zero(divisor):
        raise ZeroDivisionError("Divisão por zero.")
    quociente: list[int] = []
    resto = [0]
    for digito in dividendo:
        resto = _normalizar(resto + [digito])
        digito_quociente = 0
        candidato = base - 1
        while candidato > 0:
            produto = _multiplicar_lista_por_fator(divisor, candidato, base)
            if _comparar(produto, resto) <= 0:
                digito_quociente = candidato
                resto = _subtrair_grandes(resto, produto, base)
                break
            candidato -= 1
        quociente.append(digito_quociente)
    return _normalizar(quociente), _normalizar(resto)


def _validar_base(base: int) -> None:
    if isinstance(base, bool) or not isinstance(base, int) or not 2 <= base <= 40:
        raise ErroConversao("A base deve ser um número inteiro entre 2 e 40.")


def _analisar_numero(numero: str, base: int) -> tuple[int, list[int], int]:
    _validar_base(base)
    if not isinstance(numero, str):
        raise ErroConversao("O número deve ser informado como texto.")
    numero = numero.strip()
    if not numero:
        raise ErroConversao("O número não pode estar vazio.")
    sinal = 1
    if numero[0] in "+-":
        sinal = -1 if numero[0] == "-" else 1
        numero = numero[1:]
    if not numero:
        raise ErroConversao("O sinal deve ser acompanhado por um número.")
    if numero.count(".") > 1:
        raise ErroConversao("O número pode conter somente um ponto fracionário.")
    partes = numero.split(".")
    if any(parte == "" for parte in partes):
        raise ErroConversao("Informe dígitos antes e depois do ponto.")
    casas = len(partes[1]) if len(partes) == 2 else 0
    digitos: list[int] = []
    for simbolo in "".join(partes):
        if simbolo not in _VALORES:
            raise ErroConversao("Caractere inválido: " + simbolo)
        valor = _VALORES[simbolo]
        if valor >= base:
            raise ErroConversao(
                "O caractere '" + simbolo + "' não existe na base " + str(base) + "."
            )
        digitos.append(valor)
    return sinal, digitos, casas


def _converter_para_base_destino(
    numero: str, base_origem: int, base_trabalho: int
) -> _Fracao:
    """Usa Horner para construir uma fração exata na base de destino."""
    sinal, digitos_origem, casas = _analisar_numero(numero, base_origem)
    _validar_base(base_trabalho)
    # Método de Horner: acumula diretamente na base de trabalho.
    acumulador = [0]
    for digito in digitos_origem:
        acumulador = _multiplicar_lista_por_fator(acumulador, base_origem, base_trabalho)
        acumulador = _somar_coeficiente_na_lista(acumulador, digito, base_trabalho)
    denominador = [1]
    for _ in range(casas):
        denominador = _multiplicar_lista_por_fator(
            denominador, base_origem, base_trabalho
        )
    if _zero(acumulador):
        sinal = 0
    # Ao terminar Horner, o acumulador é o numerador da fração convertida.
    return _Fracao(sinal, acumulador, denominador)


def _gerar_texto_resultado(fracao: _Fracao, base: int) -> Resultado:
    """Gera os símbolos da parte inteira e de até dez casas fracionárias."""
    parte_inteira, resto = _dividir_grandes(
        fracao.numerador, fracao.denominador, base
    )
    texto_inteiro = "".join(ALFABETO[digito] for digito in parte_inteira)
    casas: list[str] = []
    while not _zero(resto) and len(casas) < PRECISAO_FRACIONARIA:
        resto = resto + [0]  # multiplicação pela própria base
        digito, resto = _dividir_grandes(resto, fracao.denominador, base)
        casas.append(ALFABETO[digito[-1]])
    truncado = not _zero(resto)
    while casas and casas[-1] == "0":
        casas.pop()
    texto = texto_inteiro
    if casas:
        texto += "." + "".join(casas)
    if fracao.sinal < 0 and not _zero(fracao.numerador):
        texto = "-" + texto
    return Resultado(texto, truncado)


def converter(numero: str, base_origem: int, base_destino: int) -> Resultado:
    """Converte diretamente um número entre duas bases de 2 a 40."""
    fracao_convertida = _converter_para_base_destino(
        numero, base_origem, base_destino
    )
    return _gerar_texto_resultado(fracao_convertida, base_destino)


def somar(numero1: str, base1: int, numero2: str, base2: int) -> Resultado:
    """Soma dois números e devolve o resultado na base do primeiro."""
    primeira = _converter_para_base_destino(numero1, base1, base1)
    segunda = _converter_para_base_destino(numero2, base2, base1)
    esquerda = _multiplicar_listas_de_digitos(primeira.numerador, segunda.denominador, base1)
    direita = _multiplicar_listas_de_digitos(segunda.numerador, primeira.denominador, base1)
    denominador = _multiplicar_listas_de_digitos(
        primeira.denominador, segunda.denominador, base1
    )
    if primeira.sinal == 0:
        sinal, numerador = segunda.sinal, direita
    elif segunda.sinal == 0:
        sinal, numerador = primeira.sinal, esquerda
    elif primeira.sinal == segunda.sinal:
        sinal = primeira.sinal
        numerador = _somar_listas_de_digitos(esquerda, direita, base1)
    else:
        comparacao = _comparar(esquerda, direita)
        if comparacao == 0:
            sinal, numerador = 0, [0]
        elif comparacao > 0:
            sinal = primeira.sinal
            numerador = _subtrair_grandes(esquerda, direita, base1)
        else:
            sinal = segunda.sinal
            numerador = _subtrair_grandes(direita, esquerda, base1)
    return _gerar_texto_resultado(_Fracao(sinal, numerador, denominador), base1)


def multiplicar(numero1: str, base1: int, numero2: str, base2: int) -> Resultado:
    """Multiplica dois números e devolve o resultado na base do primeiro."""
    primeira = _converter_para_base_destino(numero1, base1, base1)
    segunda = _converter_para_base_destino(numero2, base2, base1)
    numerador = _multiplicar_listas_de_digitos(primeira.numerador, segunda.numerador, base1)
    denominador = _multiplicar_listas_de_digitos(
        primeira.denominador, segunda.denominador, base1
    )
    sinal = 0 if _zero(numerador) else primeira.sinal * segunda.sinal
    return _gerar_texto_resultado(_Fracao(sinal, numerador, denominador), base1)
