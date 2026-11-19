import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_TOKEN, VIP_GROUP_ID
from handlers import start, button_handler
from database import inicializar_banco, buscar_expirados, marcar_como_removido

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def verificar_assinaturas_expiradas(context: ContextTypes.DEFAULT_TYPE):
    expirados = buscar_expirados()
    for user_id, nome, invite_link in expirados:
        try:
            # Revoga o link de convite caso o usuário ainda não tenha entrado
            if invite_link:
                try:
                    await context.bot.revoke_chat_invite_link(
                        chat_id=VIP_GROUP_ID,
                        invite_link=invite_link
                    )
                except Exception:
                    pass  # Já expirado automaticamente pelo Telegram ou já revogado

            # Ban seguido de Unban remove o membro sem bloqueá-lo de voltar se renovar
            await context.bot.ban_chat_member(chat_id=VIP_GROUP_ID, user_id=user_id)
            await context.bot.unban_chat_member(chat_id=VIP_GROUP_ID, user_id=user_id)
            marcar_como_removido(user_id)

            logger.info(f"Usuário {nome} ({user_id}) removido e link revogado por expiração.")

            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⏳ <b>Sua assinatura do Grupo VIP expirou!</b>\n\n"
                        "Seu link de acesso foi invalidado e você foi removido do grupo. "
                        "Para renovar seu acesso agora mesmo, envie /start."
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Erro ao remover usuário expirado {user_id}: {e}")


def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN não encontrado no arquivo .env")

    inicializar_banco()

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Verifica assinaturas expiradas a cada 15 segundos (ideal para testar o plano de 1 min)
    application.job_queue.run_repeating(
        verificar_assinaturas_expiradas,
        interval=15,
        first=10
    )

    print("🚀 bot_TelegramVendas rodando com controle de vencimento ativo...")
    application.run_polling()


if __name__ == "__main__":
    main()