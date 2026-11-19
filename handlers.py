from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PLANOS, VIP_GROUP_ID
from database import registrar_assinatura, obter_nova_expiracao


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton(f"⏱️ {PLANOS['teste_1min']['nome']} - R$ {PLANOS['teste_1min']['valor']:.2f}", callback_data="plano_teste_1min")],
        [InlineKeyboardButton(f"📅 {PLANOS['mensal']['nome']} - R$ {PLANOS['mensal']['valor']:.2f}", callback_data="plano_mensal")],
        [InlineKeyboardButton(f"🔥 {PLANOS['trimestral']['nome']} - R$ {PLANOS['trimestral']['valor']:.2f} (10% OFF)", callback_data="plano_trimestral")],
        [InlineKeyboardButton(f"👑 {PLANOS['semestral']['nome']} - R$ {PLANOS['semestral']['valor']:.2f} (15% OFF)", callback_data="plano_semestral")],
    ]
    reply_markup = InlineKeyboardMarkup(teclado)

    texto = (
        "👋 Bem-vindo ao <b>BotMaicoVip</b>!\n\n"
        "Escolha um dos planos abaixo para liberar seu acesso imediato ao <b>Grupo VIP</b>:\n\n"
        f"• <b>Teste Rápido:</b> R$ {PLANOS['teste_1min']['valor']:.2f} <i>(1 minuto)</i>\n"
        f"• <b>Mensal:</b> R$ {PLANOS['mensal']['valor']:.2f}\n"
        f"• <b>Trimestral:</b> R$ {PLANOS['trimestral']['valor']:.2f} <i>(10% de desconto)</i>\n"
        f"• <b>Semestral:</b> R$ {PLANOS['semestral']['valor']:.2f} <i>(15% de desconto)</i>"
    )

    await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("plano_"):
        chave_plano = data.replace("plano_", "")
        plano = PLANOS[chave_plano]

        teclado = [
            [InlineKeyboardButton("✅ [TESTE] Simular Pagamento Aprovado", callback_data=f"aprovar_{chave_plano}")],
            [InlineKeyboardButton("⬅️ Voltar aos planos", callback_data="voltar_planos")]
        ]
        reply_markup = InlineKeyboardMarkup(teclado)

        texto = (
            f"🛒 <b>Resumo do Pedido</b>\n\n"
            f"<b>Plano:</b> {plano['nome']}\n"
            f"<b>Valor:</b> R$ {plano['valor']:.2f}\n\n"
            f"Clique no botão abaixo para simular a confirmação do Pix:"
        )
        await query.edit_message_text(texto, reply_markup=reply_markup, parse_mode="HTML")

    elif data == "voltar_planos":
        teclado = [
            [InlineKeyboardButton(f"⏱️ {PLANOS['teste_1min']['nome']} - R$ {PLANOS['teste_1min']['valor']:.2f}", callback_data="plano_teste_1min")],
            [InlineKeyboardButton(f"📅 {PLANOS['mensal']['nome']} - R$ {PLANOS['mensal']['valor']:.2f}", callback_data="plano_mensal")],
            [InlineKeyboardButton(f"🔥 {PLANOS['trimestral']['nome']} - R$ {PLANOS['trimestral']['valor']:.2f} (10% OFF)", callback_data="plano_trimestral")],
            [InlineKeyboardButton(f"👑 {PLANOS['semestral']['nome']} - R$ {PLANOS['semestral']['valor']:.2f} (15% OFF)", callback_data="plano_semestral")],
        ]
        await query.edit_message_text(
            "Escolha um dos planos abaixo para liberar seu acesso ao <b>Grupo VIP</b>:",
            reply_markup=InlineKeyboardMarkup(teclado),
            parse_mode="HTML"
        )

    elif data.startswith("aprovar_"):
        chave_plano = data.replace("aprovar_", "")
        plano = PLANOS[chave_plano]
        user = query.from_user

        try:
            # 1. Calcula o momento exato de vencimento da assinatura
            data_exp = obter_nova_expiracao(
                user_id=user.id,
                dias=plano.get("dias", 0),
                minutos=plano.get("minutos", 0)
            )

            # 2. Cria link único que expira automaticamente na mesma data/hora do plano
            convite = await context.bot.create_chat_invite_link(
                chat_id=VIP_GROUP_ID,
                name=f"VIP - {user.first_name} ({user.id})",
                expire_date=data_exp,
                member_limit=1
            )

            # 3. Registra assinatura + link no SQLite
            registrar_assinatura(
                user_id=user.id,
                nome=user.full_name,
                plano=plano["nome"],
                invite_link=convite.invite_link,
                data_expiracao=data_exp
            )

            data_formatada = data_exp.strftime("%d/%m/%Y às %H:%M:%S")

            texto = (
                f"🎉 <b>Pagamento Aprovado!</b>\n\n"
                f"<b>Plano:</b> {plano['nome']}\n"
                f"<b>Válido até:</b> {data_formatada}\n\n"
                f"🔗 <b>Seu link exclusivo (uso único e válido apenas durante sua assinatura):</b>\n"
                f"{convite.invite_link}\n\n"
                f"<i>⚠️ Tanto o link quanto seu acesso expiram automaticamente em {data_formatada}.</i>"
            )
            await query.edit_message_text(texto, parse_mode="HTML")

        except Exception as e:
            texto_erro = (
                "⚠️ <b>Não foi possível gerar o link do Grupo VIP.</b>\n\n"
                "Verifique se o <code>VIP_GROUP_ID</code> no <code>.env</code> está correto e se o bot "
                "é <b>Administrador</b> do grupo com permissão para <i>Add Users</i>.\n\n"
                f"Detalhe técnico: <code>{e}</code>"
            )
            await query.edit_message_text(texto_erro, parse_mode="HTML")