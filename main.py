"""Interface de console do conversor de bases."""

from base_converter import ErroConversao, Resultado, converter, multiplicar, somar


def _ler_base(mensagem: str) -> int:
    """Lê a base, que é um parâmetro e não uma conversão intermediária."""
    texto = input(mensagem).strip()
    try:
        return int(texto)
    except ValueError as erro:
        raise ErroConversao("A base deve ser um número inteiro entre 2 e 40.") from erro


def _mostrar_resultado(resultado: Resultado, base: int) -> None:
    print("Resultado na base " + str(base) + ": " + resultado.texto)
    if resultado.truncado:
        print("Resultado truncado em 10 casas.")


def _converter() -> None:
    numero = input("Número: ").strip()
    base_origem = _ler_base("Base de origem (2 a 40): ")
    base_destino = _ler_base("Base de destino (2 a 40): ")
    _mostrar_resultado(converter(numero, base_origem, base_destino), base_destino)


def _calcular(operacao: str) -> None:
    numero1 = input("Primeiro número: ").strip()
    base1 = _ler_base("Base do primeiro número (2 a 40): ")
    numero2 = input("Segundo número: ").strip()
    base2 = _ler_base("Base do segundo número (2 a 40): ")
    if operacao == "soma":
        resultado = somar(numero1, base1, numero2, base2)
    else:
        resultado = multiplicar(numero1, base1, numero2, base2)
    _mostrar_resultado(resultado, base1)


def executar_menu() -> None:
    while True:
        print("\n=== CONVERSOR DE BASES ===")
        print("1 - Converter um número")
        print("2 - Somar dois números")
        print("3 - Multiplicar dois números")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Programa encerrado.")
            return
        try:
            if opcao == "1":
                _converter()
            elif opcao == "2":
                _calcular("soma")
            elif opcao == "3":
                _calcular("multiplicacao")
            else:
                print("Opção inválida. Escolha 0, 1, 2 ou 3.")
        except ErroConversao as erro:
            print("Erro: " + str(erro))


if __name__ == "__main__":
    executar_menu()
