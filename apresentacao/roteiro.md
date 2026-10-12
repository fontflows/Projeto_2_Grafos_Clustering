# Roteiro da apresentação

Transcrição do que falar em cada slide, com a explicação do que aparece na tela.
Tempo total previsto: cerca de 17 minutos (slides 1 a 15), mais perguntas.

Divisão sugerida (pode trocar à vontade):

- **Francisco:** slides 1 a 8 (dados, métodos e o experimento com k), cerca de 8 min e 30 s.
- **Vinicius:** slides 9 a 15 (resultados, achado e conclusões), cerca de 8 min e 30 s.
- **Os dois:** slides 16 a 18. O slide 19 é anexo, só se perguntarem sobre fórmulas.

Como ler este roteiro: em cada slide, **Na tela** descreve o que o público está vendo,
para vocês saberem para onde apontar. **Fala** é o texto para falar. Não precisa decorar
palavra por palavra; o importante é passar pelos mesmos pontos, na mesma ordem.

---

## Slide 1. Capa

**Quem fala:** Francisco · **Tempo:** 30 s

**Na tela:** o título "Seu celular sabe o que você está fazendo?", o subtítulo com o tema do projeto, os nossos nomes e seis bolinhas coloridas. As bolinhas são as cores das seis atividades, que vão aparecer em todas as figuras.

**Fala:**

Boa tarde. Eu sou o Francisco e este é o Vinicius. O título é uma pergunta de propósito: será que, só com os sensores de um celular, dá para descobrir o que uma pessoa está fazendo, sem ninguém dizer para o computador? A gente usou essa pergunta como fio condutor para o tema do projeto, que é comparar duas formas de encontrar grupos em dados: o clustering tradicional, com K-Means, e a detecção de comunidades em um grafo.

---

## Slide 2. Os dados

**Quem fala:** Francisco · **Tempo:** 1 min 15 s

**Na tela:** à esquerda, quatro frases sobre como os dados foram coletados. À direita, quatro números grandes: 10.299 janelas, 561 atributos, 6 atividades e 30 voluntários. Embaixo, os nomes das seis atividades.

**Fala:**

Os dados são públicos, do repositório de machine learning da UCI. Trinta voluntários, entre 19 e 48 anos, fizeram seis atividades do dia a dia com um celular preso na cintura: andar, subir escada, descer escada, ficar sentado, ficar em pé e ficar deitado.

O celular tem dois sensores. O acelerômetro mede a aceleração, inclusive a da gravidade, e por isso ele sabe se o celular está em pé ou deitado. O giroscópio mede rotação. Os dois foram lidos 50 vezes por segundo.

Esse sinal contínuo foi cortado em pedaços de 2,56 segundos, que a gente chama de janelas. Cada janela é um objeto do nosso problema, e são 10.299 janelas no total. De cada janela os autores do dataset já calcularam 561 números: médias, desvios, energia do sinal, frequências, ângulos. A gente não precisa entender cada um dos 561; o que importa é que cada janela vira um ponto em um espaço de 561 dimensões.

Cada janela também tem um rótulo, que é a atividade que a pessoa estava fazendo. Os pesquisadores filmaram tudo e anotaram à mão. Um detalhe importante: a gente não usa esses rótulos para agrupar. Eles só entram no final, para conferir se os grupos encontrados batem com a realidade.

---

## Slide 3. As duas abordagens

**Quem fala:** Francisco · **Tempo:** 1 min

**Na tela:** um diagrama da esquerda para a direita. Começa em "Dados X, 10.299 × 561", passa pela padronização e se divide em dois caminhos. No de cima, K-Means gera C_cluster. No de baixo, o grafo k-NN vai para o Louvain, destacado em azul porque foi implementado por nós, e gera C_community. Embaixo está escrito que a comparação é feita com ARI e NMI.

**Fala:**

Esse é o plano do trabalho, que segue o enunciado. O primeiro passo é padronizar os 561 atributos: cada um fica com média zero e desvio um, para que nenhum atributo pese mais que outro na distância.

Depois os dados seguem dois caminhos. No de cima, o K-Means agrupa as janelas direto no espaço de atributos e gera uma partição que a gente chama de C_cluster. No de baixo, a gente transforma os dados em um grafo, ligando cada janela às janelas mais parecidas com ela, e roda um algoritmo de detecção de comunidades, o Louvain, que a gente implementou do zero. Isso gera a partição C_community.

No final, comparamos as duas partições entre si e cada uma com as atividades reais, usando duas métricas: ARI e NMI. Vou explicar as duas quando elas aparecerem.

---

## Slide 4. Como os dados se parecem

**Quem fala:** Francisco · **Tempo:** 1 min 15 s

**Na tela:** à esquerda, uma nuvem de pontos. Cada ponto é uma janela, colorida pela atividade real, com o nome de cada atividade escrito sobre ela. As atividades em movimento estão em cores quentes (laranja, vermelho, amarelo) e as paradas em cores frias (azul, verde, roxo). À direita, quatro frases curtas.

**Fala:**

Não dá para desenhar 561 dimensões, então para visualizar a gente usou o t-SNE. É um método que comprime os dados para duas dimensões tentando manter perto, no desenho, os pontos que estão perto nos dados originais. Um cuidado: o t-SNE é só para desenhar. Nenhum dos algoritmos usa essas coordenadas; eles trabalham sempre nos 561 atributos.

Cada ponto é uma janela, e a cor é a atividade real. Dá para ver três coisas. Primeiro, as atividades paradas ficam à esquerda e as em movimento à direita, bem separadas. Segundo, Sentado, em azul, e Em pé, em verde, ficam completamente misturados. Faz sentido: com o celular na cintura, ficar sentado ou em pé muda muito pouco o sinal. Terceiro, Andando, em laranja, aparece quebrado em várias ilhas pequenas. Guardem essas ilhas, porque elas vão voltar no final da apresentação.

---

## Slide 5. K-Means: quantos grupos?

**Quem fala:** Francisco · **Tempo:** 1 min 15 s

**Na tela:** dois gráficos de linha com K de 2 a 10 no eixo horizontal. O da esquerda é o método do cotovelo (J, a soma das distâncias ao quadrado, em milhões). O da direita é a silhueta média. Os dois têm uma linha tracejada em K = 6. À direita, em destaque, "K = 2, maior silhueta (0,39)". Embaixo, duas frases.

**Fala:**

O K-Means precisa que a gente diga quantos grupos procurar, o K. Ele escolhe K centros e repete dois passos: cada ponto vai para o centro mais próximo, e cada centro vira a média dos seus pontos. O objetivo é deixar a soma das distâncias de cada ponto ao seu centro, que é o J, a menor possível.

Testamos K de 2 a 10. No gráfico da esquerda, o J sempre cai quando K aumenta, o que é esperado, e a ideia do cotovelo é procurar onde ele para de cair rápido. Aqui não tem uma dobra clara.

No gráfico da direita está a silhueta, que mede se os grupos são compactos e bem separados. Ela vai de menos um a um, e quanto maior, melhor. O máximo é em K igual a 2, com 0,39, e depois ela despenca. E o que o K-Means faz com K igual a 2? Ele separa "em movimento" de "parado" quase perfeitamente: o ARI dessa divisão é 0,99. Então a estrutura mais forte desses dados é essa divisão em duas.

Mesmo assim, para as comparações a gente usou K igual a 6, que é o número de atividades. O enunciado permite escolher K por conhecimento prévio, e a pergunta que nos interessa é quanto das seis atividades o K-Means consegue recuperar.

---

## Slide 6. O grafo k-NN

**Quem fala:** Francisco · **Tempo:** 1 min 15 s

**Na tela:** à esquerda, o grafo inteiro com k = 10, desenhado em cima das posições do t-SNE: pontos coloridos pela atividade e arestas em cinza claro (são 80.057 arestas). Um quadrado marca a região de Andando. No meio, o zoom desse quadrado, onde dá para ver as ilhas laranja bem ligadas por dentro. À direita, quatro frases.

**Fala:**

Agora o segundo caminho, o grafo. Cada janela vira um vértice. Para cada janela, a gente acha as k janelas mais próximas pela distância euclidiana e liga uma à outra. O grafo é simétrico: se A escolheu B como vizinho ou B escolheu A, existe aresta.

Cada aresta tem um peso gaussiano, que é essa fórmula aqui: o peso é a exponencial de menos a distância ao quadrado sobre dois sigma ao quadrado. Na prática, vizinhos muito próximos têm peso perto de um, e vizinhos mais distantes, peso menor. O sigma a gente escolheu como a mediana das distâncias entre vizinhos, uma regra simples que se ajusta sozinha à escala dos dados.

A figura mostra o grafo com k igual a 10. No zoom, à direita, dá para ver que cada ilha de Andando é bem ligada por dentro e tem poucas ligações com as outras. É exatamente esse tipo de estrutura que um algoritmo de comunidades procura.

---

## Slide 7. Louvain, implementado por nós

**Quem fala:** Francisco · **Tempo:** 1 min 30 s

**Na tela:** à esquerda, dois cartões com as duas fases do algoritmo: "1. Mover vértices" e "2. Agregar". À direita, uma tabela comparando a modularidade Q da nossa implementação com a do networkx, no grafo do clube de karatê e nos grafos k-NN com k de 3 a 20. Os valores são praticamente iguais.

**Fala:**

O algoritmo de comunidades que a gente implementou é o Louvain, em Python puro, com umas 90 linhas. Ele tenta maximizar a modularidade, o Q. A modularidade compara quantas arestas existem dentro das comunidades com quantas existiriam se as arestas fossem sorteadas ao acaso, mantendo o grau de cada vértice. Quanto mais arestas dentro do que o acaso daria, maior o Q.

O algoritmo tem duas fases. Na primeira, cada vértice começa sozinho na sua comunidade. Aí a gente passa por todos os vértices e, para cada um, calcula quanto o Q subiria se ele fosse para a comunidade de cada vizinho; ele vai para a melhor. Isso se repete até ninguém mais mudar. Na segunda fase, cada comunidade vira um único vértice, e o peso entre duas comunidades é a soma dos pesos das arestas entre elas. Aí o algoritmo volta para a primeira fase nesse grafo menor, até o Q parar de subir.

Para ter certeza de que a implementação está certa, comparamos com o Louvain da biblioteca networkx. No clube de karatê, um grafo clássico de 34 pessoas, a partição sai idêntica. Nos nossos grafos, a modularidade é praticamente a mesma, como mostra a tabela. As partições não são idênticas porque o Louvain depende da ordem em que visita os vértices, que é aleatória, mas a qualidade é a mesma.

---

## Slide 8. Experimento: variando k

**Quem fala:** Francisco · **Tempo:** 1 min

**Na tela:** a tabela do experimento. Cada linha é um valor de k: 3, 5, 10, 15 e 20, que são os do enunciado, mais 30, 50, 100, 200 e 400. As colunas são grau médio, número de comunidades, modularidade Q, ARI e NMI. A linha de k = 100 está destacada em azul.

**Fala:**

Essa é a tabela que o enunciado pede. Além dos valores 3, 5, 10, 15 e 20, a gente acrescentou 30, 50, 100, 200 e 400, para conseguir ver o que acontece nos extremos.

Como o Louvain tem uma parte aleatória, cada valor da tabela é a média de cinco execuções com sementes diferentes, e o número depois do "mais ou menos" é o desvio-padrão. Os desvios são pequenos, então os resultados são estáveis.

O ARI e o NMI aqui comparam as comunidades com as atividades reais. Os dois valem um quando as partições são iguais. O ARI conta pares de pontos que estão juntos ou separados nas duas partições e desconta o que o acaso daria; o NMI mede quanto saber o grupo de um ponto em uma partição ajuda a adivinhar o grupo dele na outra.

A linha destacada é k igual a 100, que é o valor que a gente usa nas comparações. O Vinicius vai mostrar por quê.

---

## Slide 9. O que k muda

**Quem fala:** Vinicius · **Tempo:** 1 min 30 s

**Na tela:** quatro gráficos em grade, todos com k no eixo horizontal em escala logarítmica e uma linha tracejada em k = 100. Em cima à esquerda, o grau médio; em cima à direita, o número de comunidades; embaixo à esquerda, a modularidade Q; embaixo à direita, o ARI, com uma linha azul (contra a atividade real) e uma laranja (contra o K-Means). Os pontos têm barras de erro. À direita, três cartões: k pequeno, k = 100 e k muito grande.

**Fala:**

Esses gráficos respondem as perguntas do enunciado sobre k.

Primeiro, a densidade. O grau médio, em cima à esquerda, cresce praticamente proporcional a k: vai de uns 5 com k igual a 3 até mais de 600 com k igual a 400.

Segundo, o número de comunidades, em cima à direita. Ele cai rápido: umas 55 com k igual a 3, umas 27 com k igual a 10 e chega a 5 com k igual a 400.

Terceiro, a modularidade, embaixo à esquerda, cai o tempo todo. Com mais arestas fica mais difícil ter comunidades isoladas.

E qual é o melhor k? Depende do critério. Se a gente olhar só para o Q, o melhor seria k igual a 3. Mas aí são 55 comunidades, que são pedaços das atividades. Olhando a concordância com as atividades reais, que é a linha azul embaixo à direita, o melhor fica entre 50 e 100, e o máximo é em 100, com ARI de 0,55. Por isso escolhemos k igual a 100.

Quando k é muito pequeno, o grafo fica fragmentado e enxerga detalhe demais, como vamos ver no final. Quando k é muito grande, as vizinhanças passam a incluir janelas de outras atividades: com 400, andar, subir e descer escada viram uma comunidade só, e o ARI cai. A lição é que Q alto não garante grupos com significado.

---

## Slide 10. Atividade real × K-Means × comunidades

**Quem fala:** Vinicius · **Tempo:** 1 min

**Na tela:** três mapas t-SNE lado a lado, com os mesmos pontos nas mesmas posições. À esquerda, a cor é a atividade real. No meio, os grupos do K-Means com K = 6. À direita, as comunidades do Louvain com k = 100. Nos dois últimos, cada grupo recebe a cor da atividade mais comum dentro dele, em tons diferentes quando dois grupos têm a mesma atividade majoritária.

**Fala:**

Aqui está a comparação visual. Os pontos estão nas mesmas posições nos três mapas; o que muda é a cor. À esquerda, a verdade. No meio, o K-Means. À direita, as comunidades. Para facilitar a comparação, cada grupo recebe a cor da atividade mais comum dentro dele.

As duas abordagens acertam o grosso: Deitado, em roxo, sai certinho nos dois, e movimento e parado ficam separados. Nenhuma das duas consegue separar Sentado de Em pé. As duas cortam aquela nuvem do lado esquerdo em dois pedaços, mas o corte não segue a fronteira entre as atividades. No lado em movimento, o grafo isola Subindo escada, em vermelho, bem melhor que o K-Means, que mistura as três atividades.

---

## Slide 11. O que tem dentro de cada grupo

**Quem fala:** Vinicius · **Tempo:** 1 min 15 s

**Na tela:** duas tabelas coloridas lado a lado, uma para o K-Means e outra para as comunidades. Cada linha é um grupo e cada coluna é uma atividade. O número em cada célula é quantas janelas daquela atividade caíram naquele grupo, e quanto mais escuro o azul, maior a fração do grupo.

**Fala:**

Essa figura mostra a composição de cada grupo: cada linha é um grupo, cada coluna é uma atividade, e o número diz quantas janelas daquela atividade caíram ali. Se a partição fosse perfeita, a gente veria uma diagonal escura.

Deitado é quase perfeito nos dois: no K-Means, 1.557 janelas no último grupo; nas comunidades, 1.831 das 1.860 janelas de Deitado ficaram na comunidade 6.

Nas comunidades, Andando e Descendo escada ficaram juntos na comunidade 1, e Subindo escada ficou quase sozinho na comunidade 2. No K-Means, as três atividades em movimento estão espalhadas pelos três primeiros grupos. E nos dois métodos, Sentado e Em pé aparecem misturados em duas linhas.

Tem um detalhe curioso: a comunidade 3 tem só duas janelas. São duas janelas seguidas do voluntário 19 descendo a escada, que estão muito longe de todas as outras. Como o peso gaussiano cai muito com a distância, as arestas delas para o resto têm peso praticamente zero, e elas ficam ligadas só entre si. Ou seja, o Louvain isolou um outlier sozinho.

---

## Slide 12. Comparação com as atividades reais

**Quem fala:** Vinicius · **Tempo:** 1 min 15 s

**Na tela:** em cima, a tabela com as três comparações pedidas no enunciado, com ARI e NMI. Embaixo, a tabela de silhueta das três partições. À direita, três frases.

**Fala:**

Esses são os números das três comparações que o enunciado pede.

Contra as atividades reais, as comunidades vão melhor que o K-Means nas duas métricas: ARI de 0,54 contra 0,42, e NMI de 0,66 contra 0,56. Entre si, os dois métodos concordam razoavelmente, com ARI de 0,61. Ou seja, eles acertam a mesma divisão grossa e erram no mesmo lugar, que é Sentado contra Em pé.

A silhueta, na tabela de baixo, conta uma história diferente. Ela é maior para o K-Means, mas isso é esperado, porque o K-Means otimiza justamente grupos compactos, que é o que a silhueta mede. O mais interessante é a silhueta das próprias atividades reais: 0,03, quase zero. Isso quer dizer que, no espaço de atributos, as atividades não formam bolas compactas e separadas. E é por isso que um método baseado em vizinhança, como o grafo, se sai melhor que um método baseado em centros, como o K-Means.

---

## Slide 13. Onde os dois métodos erram

**Quem fala:** Vinicius · **Tempo:** 1 min 15 s

**Na tela:** um mapa t-SNE em que cada ponto tem uma de quatro cores. Cinza: os dois métodos acertam. Laranja: só o K-Means erra. Azul: só as comunidades erram. Preto: os dois erram. À direita, dois números: 19%, para os pontos que os dois erram, e 5%, para os que os dois acertam.

**Fala:**

A gente quis ver onde exatamente os métodos erram. Para isso, cada grupo recebe o nome da atividade mais comum dentro dele, e uma janela conta como acerto quando a atividade do seu grupo é a atividade real dela.

No mapa, cinza são as janelas que os dois acertam, e preto as que os dois erram. Os pontos pretos se concentram na região de Sentado e Em pé e nas bordas entre as atividades em movimento.

Para medir isso, para cada janela a gente olhou as 10 vizinhas mais próximas e contou quantas são de outra atividade. Nas janelas que os dois métodos erram, em média 19% das vizinhas são de outra atividade. Nas que os dois acertam, só 5%. Então os dois erram exatamente onde os próprios dados são ambíguos, nas fronteiras.

---

## Slide 14. Achado: o jeito de andar é pessoal

**Quem fala:** Vinicius · **Tempo:** 1 min 30 s

**Na tela:** um gráfico de barras horizontais, uma barra por atividade, com a porcentagem das 10 vizinhas mais próximas que são da mesma pessoa. Um tracinho preto em cada barra marca o valor esperado ao acaso, por volta de 3%. À direita, dois números: 94%, para Andando, e 90%, para Andando ignorando janelas próximas no tempo.

**Fala:**

Agora o resultado que mais surpreendeu a gente. Lembram das ilhas de Andando? A gente se perguntou o que elas eram.

Para cada janela, olhamos as 10 janelas mais parecidas e contamos quantas são da mesma pessoa. Como são 30 pessoas, ao acaso seria uns 3%, que é esse tracinho preto. Para Andando, o resultado é 94%. Para Sentado e Em pé, fica perto de 25%.

Como as janelas se sobrepõem no tempo, a gente desconfiou que isso podia ser só porque janelas seguidas são parecidas. Então refizemos a conta ignorando as vizinhas que estão a até 5 janelas de distância no tempo. Andando ainda dá 90%, enquanto Sentado cai para 10%.

Ou seja: parado, todo mundo é parecido; andando, cada pessoa tem um ritmo e um balanço próprios, quase uma impressão digital. O grafo enxerga isso. Com k pequeno, as comunidades dentro de Andando correspondem a pessoas, e não a atividades. É a mesma ideia de pesquisas que identificam pessoas pelo jeito de andar.

---

## Slide 15. Conclusões

**Quem fala:** Vinicius · **Tempo:** 1 min

**Na tela:** quatro cartões, um para cada conclusão.

**Fala:**

Para fechar, quatro conclusões.

Primeira: as duas abordagens concordam no grosso. Movimento contra parado e a classe Deitado aparecem nas duas, e o ARI entre elas é 0,61.

Segunda: as comunidades recuperam as atividades um pouco melhor, com NMI de 0,66 contra 0,56 do K-Means, porque o grafo trabalha com vizinhança e não exige que os grupos sejam bolas em torno de um centro.

Terceira: o k do grafo funciona como um controle de escala. k pequeno enxerga detalhes, como as pessoas; k grande enxerga só o geral. E modularidade alta sozinha não garante grupos úteis.

Quarta: os grupos naturais dos dados nem sempre são os rótulos que alguém escolheu. Aqui apareceram duas estruturas que ninguém pediu: a divisão entre movimento e parado, e as próprias pessoas.

---

## Slide 16. Referências

**Quem fala:** qualquer um · **Tempo:** 5 s

**Na tela:** a lista de referências.

**Fala:**

Essas são as referências que usamos, a começar pelo artigo original do Louvain e pelos trabalhos sobre modularidade e comparação de partições.

---

## Slide 17. Obrigado

**Quem fala:** Francisco · **Tempo:** 10 s

**Na tela:** "Obrigado!" e a linha "Código, figuras e tabelas: um comando, python src/main.py".

**Fala:**

Obrigado pela atenção. Todo o código roda com um único comando, e as sementes são fixas, então qualquer pessoa consegue reproduzir exatamente esses resultados.

---

## Slide 18. Perguntas

**Quem fala:** os dois · **Tempo:** o que sobrar

**Na tela:** "Perguntas?".

**Fala:**

Ficamos à disposição para perguntas.

---

## Slide 19. Anexo: as medidas usadas

**Quem fala:** quem receber a pergunta · **Tempo:** só se perguntarem

**Na tela:** quatro cartões com a modularidade, o ganho de mover um vértice no Louvain, o ARI e o NMI.

**Fala:**

A modularidade compara a fração de arestas dentro das comunidades com a fração esperada ao acaso, mantendo os graus. No Louvain, o ganho de mover um vértice i para uma comunidade C tem dois termos: o peso das arestas de i para C, que é bom, menos o que seria esperado ao acaso, que é a soma dos graus de C vezes o grau de i, dividido por 2m. O ARI conta pares de pontos que estão juntos ou separados nas duas partições e desconta o acaso. O NMI mede a informação que as duas partições compartilham, normalizada entre zero e um.

---

## Perguntas prováveis e respostas curtas

**Por que Louvain e não Girvan-Newman ou Label Propagation?**
Girvan-Newman recalcula a intermediação de todas as arestas a cada remoção, o que seria lento demais com 80 mil a 3 milhões de arestas. Label Propagation não otimiza nenhuma medida e oscila bastante em grafos k-NN. O Louvain otimiza a modularidade, que o enunciado pede, e roda em segundos.

**Como vocês sabem que a implementação está certa?**
Comparamos com o networkx: no karatê a partição é idêntica, e nos grafos k-NN a modularidade é praticamente a mesma. Também calculamos o Q da nossa partição com a função do networkx e ele bate com o nosso.

**Escolher k = 100 olhando o ARI não é usar os rótulos?**
É, e a gente assume isso: o k foi escolhido para responder a pergunta do enunciado sobre qual k dá os melhores resultados. O K-Means também usou os rótulos para escolher K = 6. A comparação entre os dois é justa nesse sentido. Sem rótulos, a escolha teria que ser pela estabilidade ou pela modularidade, e a modularidade sozinha escolheria k pequeno demais.

**A fórmula de Q do enunciado usa A_ij de 0 e 1. Vocês usaram pesos?**
Sim. Usamos a versão ponderada, que é a mesma fórmula com A_ij igual ao peso da aresta, k_i igual à soma dos pesos das arestas de i e m igual à soma de todos os pesos. Com todos os pesos iguais a 1 ela vira exatamente a fórmula do enunciado. O networkx calcula do mesmo jeito, e foi contra ele que validamos.

**Por que o grafo desenhado é com k = 10 e não k = 100?**
Com k = 100 são mais de 800 mil arestas, e o desenho vira uma mancha cinza. Com k = 10 dá para ver a estrutura. A construção é a mesma, só muda o k.

**Por que os resultados mudam com a semente?**
O Louvain visita os vértices em ordem aleatória e as escolhas dependem dessa ordem. Por isso rodamos 5 sementes; o desvio é pequeno.

**O que o Leiden melhora?**
O Louvain pode gerar comunidades mal conectadas por dentro. O Leiden (Traag, Waltman e van Eck, 2019) adiciona uma fase de refinamento que garante comunidades conectadas.

**Quais as limitações da modularidade?**
Limite de resolução: comunidades pequenas podem ser fundidas mesmo sendo bem definidas (Fortunato e Barthélemy, 2007). E Q alto não garante significado: o maior Q do nosso experimento foi o pior contra os rótulos.

**O t-SNE influencia o resultado?**
Não. Só é usado para desenhar.

**Por que padronizar se os dados já estão entre −1 e 1?**
Estar no mesmo intervalo não quer dizer ter a mesma variância. Sem padronizar, atributos que variam mais dominariam a distância.

**Por que sigma igual à mediana das distâncias?**
É uma escala típica de distância entre vizinhos. Com sigma muito pequeno quase todos os pesos seriam zero; muito grande, todos seriam um.
