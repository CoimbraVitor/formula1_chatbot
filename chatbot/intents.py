def get_f1_intents():
    return [
        [r"1|o que é formula 1|o que é f1",
         ["A Fórmula 1 é a principal categoria do automobilismo mundial, com carros de alta performance."]],

        [r"2|o que é drs",
         ["DRS é um sistema que reduz o arrasto do carro para facilitar ultrapassagens."]],

        [r"3|o que é pit stop",
         ["Pit stop é a parada nos boxes para troca de pneus ou ajustes no carro."]],

        [r"4|quem é lewis hamilton",
         ["Lewis Hamilton é um heptacampeão mundial de Fórmula 1."]],

        [r"5|quem é max verstappen",
         ["Max Verstappen é um piloto campeão mundial conhecido por sua pilotagem agressiva."]],

        [r"oi|olá|ola",
         ["Olá! 👋\n\nO que você quer saber?\n\n"
          "1 - O que é Fórmula 1?\n"
          "2 - O que é DRS?\n"
          "3 - O que é Pit Stop?\n"
          "4 - Quem é Lewis Hamilton?\n"
          "5 - Quem é Max Verstappen?\n\n"
          "Digite o número ou a pergunta!"]],

        [r"(.+)",
         ["Não entendi muito bem 🤔\n\n"
          "Escolha uma opção:\n"
          "1 - Fórmula 1\n"
          "2 - DRS\n"
          "3 - Pit Stop\n"
          "4 - Lewis Hamilton\n"
          "5 - Verstappen"]]
    ]