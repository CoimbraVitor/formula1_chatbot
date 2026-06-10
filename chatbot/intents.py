def get_f1_intents():
    return [

        # ---------------- INÍCIO / SAUDAÇÃO ----------------
        [r"(?i)^(oi|olá|ola|menu|iniciar|bom dia|boa tarde|boa noite)[!.,\s]*$",
         ["Olá! Que bom falar com você. 👋\n\nEu sou o seu assistente de F1 e estou super empolgado para mergulharmos nesse assunto! Podemos falar sobre as regras, a tecnologia dos carros, os grandes pilotos ou o que mais você tiver curiosidade.",
          "Oi pessoal! 👋 Pronto para falar sobre o esporte mais rápido do mundo? Eu conheço bastante sobre a história da F1, o funcionamento do DRS, as trocas de pneu e os maiores campeões. Por onde quer começar?"]],

        # ---------------- AFIRMATIVO / NEGATIVO (CONVERSACIONAL) ----------------
        [r"(?i)^(sim|quero|claro|pode ser|com certeza|bora|manda|explica)[!.,\s]*$",
         ["Que legal a sua empolgação! Vou te contar todos os detalhes então. 😄",
          "Ótimo! É fascinante quando entramos mais a fundo nesses temas. Vamos lá!",
          "Excelente! Vou explicar para você agora mesmo."]],

        [r"(?i)^(não|não quero|mais tarde|depois|nada|nem)[!.,\s]*$",
         ["Tudo bem! Podemos pular para outro assunto que te interesse mais.",
          "Sem problemas! A F1 tem muitos outros temas legais para explorarmos.",
          "Entendido! O que mais você gostaria de saber então?"]],

        # ---------------- RESPOSTAS DAS PERGUNTAS GUIADAS (HOOKS) ----------------
        [r"(?i)^(detalhes técnicos|tecnico|técnico|detalhes|tecnica)[!.,\s]*$",
         ["Você é dos meus! Gosta de saber como a mágica acontece. Os carros de F1 são basicamente aviões de cabeça para baixo!",
          "A parte técnica é um universo à parte. Desde a telemetria até os materiais compostos de fibra de carbono."]],

        [r"(?i)^(emoção|acao|ação|corridas|emocionante|emocao)[!.,\s]*$",
         ["Concordo! A adrenalina das ultrapassagens e a incerteza do resultado é o que faz a F1 ser tão apaixonante.",
          "A emoção é indescritível! Ver os carros a mais de 300km/h brigando roda a roda é de tirar o fôlego."]],

        # ---------------- CONCEITOS ----------------
        [r"(?i)^o que é drs\??$|^drs\??$|^como funciona o drs\??$",
         ["O DRS (Drag Reduction System) é aquele sistema fantástico onde a asa traseira se abre para diminuir a resistência do ar. Isso dá um 'empurrãozinho' extra para facilitar as ultrapassagens nas retas!",
          "Sabe quando a asa do carro abre? Isso é o DRS! Ele reduz o arrasto aerodinâmico e permite que o carro ganhe mais velocidade final para tentar superar o adversário."]],

        [r"(?i)^o que é um? pit stop\??$|^o que são pit stops\??$",
         ["Um pit stop é pura poesia em movimento! Em menos de 3 segundos, uma equipe inteira troca os quatro pneus do carro. É um trabalho de precisão absurdo.",
          "As paradas nos boxes, ou pit stops, são momentos cruciais da estratégia. É onde a corrida pode ser ganha ou perdida em questão de milésimos!"]],

        [r"(?i)^o que é o? safety car\??$",
         ["O Safety Car entra na pista quando as condições ficam perigosas, como em acidentes ou chuva forte. Ele lidera o pelotão em velocidade reduzida para garantir a segurança de todos.",
          "Pense no Safety Car como o 'xerife' da pista. Ele mantém todo mundo na linha enquanto os fiscais limpam detritos ou resolvem algum problema no circuito."]],

        [r"(?i)^o que é qualif(ying|icação)\??$|^o que é o grid\??$",
         ["A classificação é o momento de 'pé no porão'! É quando os pilotos dão tudo de si em uma única volta para decidir quem larga na frente no domingo.",
          "Sábado é dia de Qualifying! É a disputa pela Pole Position, onde a precisão absoluta é necessária para garantir a melhor posição de largada."]],

        # ---------------- PILOTOS ----------------
        [r"(?i)^quem (é|foi) (lewis hamilton|hamilton)\??$|^(lewis hamilton|hamilton)\??$",
         ["Lewis Hamilton é simplesmente uma lenda viva! O cara tem 7 títulos mundiais e detém quase todos os recordes da categoria. Além de piloto, ele é uma voz muito importante fora das pistas.",
          "Falar de Hamilton é falar de história. Ele é um dos maiores de todos os tempos, conhecido pela sua consistência absurda e talento em condições de chuva."]],

        [r"(?i)^quem (é|foi) (max verstappen|verstappen)\??$|^(max verstappen|verstappen)\??$",
         ["Max Verstappen é o fenômeno atual! Ele trouxe uma agressividade e um talento nato que mudaram a dinâmica da Red Bull e da categoria nos últimos anos.",
          "Verstappen é pura velocidade. Ele se tornou um dos campeões mais dominantes da história recente, sempre levando o carro ao limite absoluto."]],

        [r"(?i)^quem (é|foi) (ayrton senna|senna|seninha)\??$|^(ayrton senna|senna)\??$",
         ["Ayrton Senna é, para muitos, o maior de todos os tempos. Sua velocidade bruta, carisma e pilotagem na chuva eram sobrenaturais.",
          "O Senna não era só um piloto, era um herói nacional. Sua rivalidade com Prost é o capítulo mais épico da história da F1."]],

        [r"(?i)^quem é ([\w\s]+)\?$",
         ["Ah, %1! Com certeza é um nome que deixou ou está deixando sua marca na F1. Você quer saber sobre a carreira ou sobre algum momento específico dele?",
          "%1 é uma figura interessante no grid! Sabia que cada piloto traz uma história única para a pista? O que mais te chama atenção nessa pessoa?"]],

        # ---------------- EQUIPES ----------------
        [r"(?i)^(o que é a|me fala da|ferrari)\??$|^ferrari\??$",
         ["A Ferrari é a alma da F1! Estão no grid desde 1950. Correr com o carro vermelho é o sonho de quase todo piloto.",
          "Falar de Ferrari é falar dos Tifosi e da tradição italiana. Eles passaram por períodos de glória absoluta com Schumacher e Lauda."]],

        [r"(?i)^(equipe favorita|times da f1|equipes da f1)\??$",
         ["O grid atual é muito competitivo! Temos gigantes como Ferrari, Mercedes e Red Bull, mas equipes como McLaren e Aston Martin estão dando um show também.",
          "Cada equipe tem sua própria alma. A Ferrari com sua tradição, a Red Bull com sua ousadia e a Mercedes com sua precisão alemã. Difícil escolher uma só, né?"]],

        # ---------------- PNEUS ----------------
        [r"(?i)^(o que são os? pneus|tipos de pneus|pneus da f1)\??$",
         ["Os pneus são o único ponto de contato do carro com o solo, então eles são TUDO! Temos os macios (rápidos mas duram pouco), os médios e os duros (mais lentos mas aguentam muito).",
          "A Pirelli leva diferentes compostos para cada pista. Gerenciar o desgaste dos pneus é o que separa os bons pilotos dos gênios da estratégia!"]],

        # ---------------- BANDEIRAS ----------------
        [r"(?i)^(o que significa a? |)bandeira amarela\??$",
         ["Bandeira amarela significa: 'Cuidado! Tem algo errado à frente'. Os pilotos precisam reduzir a velocidade e as ultrapassagens são proibidas no local.",
          "Avistou o amarelo? É sinal de perigo. É o momento de cautela para evitar acidentes maiores na pista."]],

        [r"(?i)^(o que significa a? |)bandeira vermelha\??$",
         ["Bandeira vermelha é o sinal de 'Parada Total'. A corrida é interrompida imediatamente e todos os carros devem voltar para os boxes.",
          "Quando o perigo é muito grande ou a pista está bloqueada, a bandeira vermelha entra em ação para garantir a integridade de todos."]],

        # ---------------- CONVERSACIONAL ----------------
        [r"(?i)^eu gosto de ([\w\s]+)$",
         ["Que legal que você gosta de %1! O que exatamente te faz curtir tanto essa parte?",
          "Interessante! %1 realmente tem seu charme na F1. Você acompanha há muito tempo?"]],

        [r"(?i)^eu não gosto de ([\w\s]+)$",
         ["Entendo perfeitamente. %1 pode ser um assunto polêmico mesmo na comunidade. O que te incomoda mais?",
          "É um ponto de vista válido! Na F1, as opiniões se dividem bastante sobre %1. Por que você se sente assim?"]],

        [r"(?i)^eu acho que ([\w\s,]+)$",
         ["Gostei da sua perspectiva sobre %1. É sempre bom debater esses pontos com quem entende do assunto!",
          "Você tem um ponto interessante! %1 é algo que muitos especialistas também discutem. Pode me contar mais do seu raciocínio?"]],

        # ---------------- INTERAÇÃO ----------------
        [r"(?i)^(como você está|tudo bem|tudo bom)[!?\s]*$",
         ["Estou melhor agora que estamos falando de corrida! E por aí, como vai a empolgação para a próxima etapa?",
          "Tudo ótimo por aqui! Sempre pronto para um bom papo sobre motores e estratégia. E você, como está hoje?"]],

        [r"(?i)^qual (é o seu|seu) nome\??$",
         ["Pode me chamar de seu Estrategista de F1! Estou aqui para ser o seu guia nesse mundo de alta velocidade. 😄"]],
    ]