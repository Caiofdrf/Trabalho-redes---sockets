# Trabalho redes - sockets

## Para o funcionamento do código:
Uma mudança importante é que, para o código do cliente funcionar e se conectar corretamente, é necessário que a variável HOST receba o valor do IPv4 da máquina que está rodando o servidor. Portanto, o código da maneira que está não funcionará em redes diferentes da utilizada nos testes.

## Explicação do código do servidor:
Basicamente a execução do código se inicia na função main, onde criamos o socket do servidor, configuramos o endereço de IP dele e a porta que será utilizada para nossa comunicação, e depois usamos listen para permitir recepção de requisições de entrada.

Após isso entramos em um while true onde todo usuário que tentar entrar no servidor será aceito e adicionado no array de usuários. Logo após isso é criada uma thread específica para cada usuário, responsável por cuidar justamente da comunicação do usuário. Essa thread executa a função player_handler.

Na função player handler é inicialmente lida uma mensagem recebida no servidor e enviada pelo usuário, após a decodificação da mensagem é visto se ela começa com "BOARD:" ou "CURRENT:", pois no inicio de todas as nossas mensagens temos um desses dois, representando os dois tipos de conteúdo trocados entre cliente e servidor no nosso sistema. Se a mensagem entra em um desses dois casos, é chamada a função broadcast que envia a mensagem para todos os usuários conectados, menos o usuário que enviou a mensagem ao servidor. 

## Explicação do código do jogador/cliente:
No inicio do código do cliente é criado o socket do jogador, utilizando TCP. Na função main, inicialmente tentamos conectar o jogador ao servidor e, após isso, geramos o tabuleiro inicial para o usuário e criamos uma thread para ele receber os tabuleiros do servidor. Após isso entramos em um while true onde é verificado alguma ação relacionada a eventos no jogo, focando em dois principais, um de sair do jogo, que finaliza o socket e desconecta o usuário do servidor, e outro para tratamento de click no tabuleiro.

Na função de tratamento de click, quandoé detectado que o usuário de fato fez um lance, nós criamos uma nova variável chamada txt_box, a qual recebe o valor retornado da função create_box. A função create box basicamente passa por todas as posições do tabuleiro, verifica se tem alguma peça nela e que peça é, e adiciona em uma string, de forma que ao passar pelo tabuleiro inteiro a string tenha um formato como "RCBQKBCRPPPPPPPPnnnnnn...". Essa string é retornada, então o valor de txt_box recebe isso.

Após o comando de send_box no handler de click, nós enviamos ao servidor quem é o player atual após o lance ser feito por meio da função send_current_player.

Após enviar o jogador atual é enviado também a txt_box com uma representação em texto de como está o tabuleiro novo após o lance.

Dessa maneira, somos capazes de representar de forma simples o estado após o lance do tabuleiro e enviar ao servidor, o qual redistribui para os demais usuários, que convertem esse formato de texto para um tabuleiro novo por meio da função de receive_table, que roda na thread de background criada no começo da main.

Na função receive_table nós lemos a mensagem recebida pelo usuário, decodificamos ela e verificamos em qual dos dois casos de mensagens ela se encaixa, em mensagens CURRENT ou mensagens BOARD. Caso seja uma mensagem do tipo CURRENT, nós dividimos a mensagem a partir do ":" e definimos a variável current_player para o que estiver escrito após o ":", ou seja, white ou black.

Caso a mensagem seja do tipo BOARD nós criamos um payload com todo o conteúdo após a mensagem "BOARD:", ou seja, seria o equivalente a pegar a string txt_box criada anteriormente. Após adquirir o payload nós criamos um tabuleiro novo e vamos preenchendo ele com as peças da maneira descrita no payload. Após o preenchimento do novo tabuleiro nós colocamos que board = n_board, ou seja, o tabuleiro atual recebe esse novo tabuleiro atualizado.

## Conclusão:
Dessa forma fomos capazes de enviar ao servidor uma mensagem com as características do tabuleiro após um movimento, onde essa mensagem é redirecionada para todos os demais jogadores, que farão a tradução dessa mensagem e atualizarão seus tabuleiros, permitindo que todos os usuários tenham o tabuleiro atualizado e possam fazer os lances com as peças corretas.


