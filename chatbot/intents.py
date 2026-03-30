def get_f1_intents():
    return [
        [r"(?i)1|o que é formula 1|o que é f1|Fórmula 1",
         ["A Fórmula 1 é a principal categoria do automobilismo mundial."]],

        [r"(?i)2|o que é drs|DRS",
         ["DRS é um sistema que ajuda nas ultrapassagens."]],

        [r"(?i)3|o que é pit stop|Pit Stop",
         ["Pit stop é a parada para troca de pneus."]],

        [r"(?i)4|quem é lewis hamilton|Lewis Hamilton",
         ["Lewis Hamilton é um heptacampeão mundial."]],

        [r"(?i)5|quem é max verstappen|Verstappen",
         ["Max Verstappen é um piloto campeão mundial."]],

        [r"(?i)oi|olá|ola",
         ["Olá! 👋\n\nEscolha uma opção:\n\n"
          "1 - O que é Fórmula 1?\n"
          "2 - O que é DRS?\n"
          "3 - O que é Pit Stop?\n"
          "4 - Quem é Lewis Hamilton?\n"
          "5 - Quem é Max Verstappen?\n"]],
        [r"(.+)",
         ["Não entendi muito bem 🤔\n\n"
          "Escolha uma opção:\n"
          "1 - Fórmula 1\n"
          "2 - DRS\n"
          "3 - Pit Stop\n"
          "4 - Lewis Hamilton\n"
          "5 - Verstappen"]]
    ]