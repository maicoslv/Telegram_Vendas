# 🤖 Bot de Vendas e Gestão de Assinaturas VIP (Telegram)

Bot automatizado desenvolvido em **Python** para comercialização de planos de acesso a grupos VIP no Telegram, com geração de links exclusivos temporários, controle de vencimentos em banco de dados e remoção automática de membros expirados.

## 🚀 Funcionalidades

- **Catálogo Interativo de Planos:** Menu com botões inline (`Mensal`, `Trimestral` e `Semestral`) e cálculo automático de descontos progressivos.
- **Links de Convite Únicos e Temporários:** Integração com `create_chat_invite_link` configurada com `member_limit=1` e `expire_date` sincronizado ao vencimento da assinatura.
- **Controle de Vigência em SQLite:** Persistência local dos assinantes (`user_id`, plano, link gerado e data de expiração), com soma automática de dias em caso de renovação antecipada.
- **Remoção e Revogação Automáticas:** Rotina assíncrona via `JobQueue` que revoga links expirados, remove assinantes vencidos (`ban` + `unban` para permitir retorno futuro) e envia notificação de renovação no privado.

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **python-telegram-bot** (v21+ com `JobQueue` assíncrono)
- **SQLite3** (persistência relacional nativa)
- **python-dotenv** (gerenciamento seguro de credenciais)

## ⚙️ Como Executar Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/telegram_vendas.git](https://github.com/maicoslv/telegram_vendas.git)
   cd telegram_vendas