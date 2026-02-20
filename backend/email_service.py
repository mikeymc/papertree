import os
import json
import resend
import logging
import smtplib
import markdown

logger = logging.getLogger(__name__)

APP_URL = os.environ.get('APP_URL', 'https://papertree.ai')

def send_verification_email(to_email: str, code: str) -> bool:
    """
    Send a verification email with the OTP code using Resend.
    
    Args:
        to_email: The recipient's email address.
        code: The 6-digit OTP code.
        
    Returns:
        bool: True if sent successfully, False otherwise.
    """
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        logger.error("RESEND_API_KEY not set. Cannot send email.")
        return False
        
    resend.api_key = api_key
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Verify your email</h2>
        <p>Thank you for signing up for papertree.ai</p>
        <p>Your verification code is:</p>
        <div style="background-color: #f4f4f5; padding: 12px; border-radius: 6px; text-align: center; margin: 20px 0;">
            <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #18181b;">{code}</span>
        </div>
        <p>This code will expire in 15 minutes.</p>
        <p>If you didn't request this code, you can safely ignore this email.</p>
    </div>
    """
    
    try:
        r = resend.Emails.send({
            "from": "Papertree AI <info@papertree.ai>",
            "to": to_email,
            "subject": "Your Verification Code",
            "html": html_content
        })
        logger.info(f"Verification email sent to {to_email}. ID: {r.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        return False


def _format_currency(value):
    """Format a number as currency."""
    if value is None:
        return '$0'
    return f"${value:,.0f}"


def _format_pct(value):
    """Format a number as percentage with sign."""
    if value is None:
        return '0.00%'
    sign = '+' if value >= 0 else ''
    return f"{sign}{value:.2f}%"


def build_briefing_html(briefing: dict, portfolio_name: str) -> str:
    """Render an HTML email from briefing data."""
    buys = json.loads(briefing.get('buys_json', '[]'))
    sells = json.loads(briefing.get('sells_json', '[]'))
    analysts = briefing.get('analysts', ['lynch', 'buffett'])
    
    is_single = len(analysts) == 1
    show_lynch = 'lynch' in analysts
    show_buffett = 'buffett' in analysts
    
    trades = []
    for b in buys:
        trades.append({
            'action': 'BUY',
            'symbol': b.get('symbol', ''),
            'shares': b.get('shares', 0),
            'price': b.get('price', 0),
            'value': b.get('position_value'),
            'lynch_score': b.get('lynch_score'),
            'buffett_score': b.get('buffett_score')
        })
    for s in sells:
        trades.append({
            'action': 'SELL',
            'symbol': s.get('symbol', ''),
            'shares': s.get('shares', 0),
            'price': s.get('price', 0),
            'value': s.get('position_value'),
            'lynch_score': s.get('lynch_score'),
            'buffett_score': s.get('buffett_score')
        })

    trades_html = ''
    if trades:
        header_html = f'''
                    <th style="padding: 8px 12px; text-align: left;">Action</th>
                    <th style="padding: 8px 12px; text-align: left;">Symbol</th>
                    <th style="padding: 8px 12px; text-align: right;">Shares</th>
                    <th style="padding: 8px 12px; text-align: right;">Price</th>
                    <th style="padding: 8px 12px; text-align: right;">Value</th>'''
        if is_single:
            header_html += '\n                    <th style="padding: 8px 12px; text-align: right;">Score</th>'
        else:
            if show_lynch:
                header_html += '\n                    <th style="padding: 8px 12px; text-align: right;">Lynch Score</th>'
            if show_buffett:
                header_html += '\n                    <th style="padding: 8px 12px; text-align: right;">Buffett Score</th>'

        rows = ''
        for t in trades:
            color = '#16a34a' if t['action'] == 'BUY' else '#dc2626'
            val_str = f"${int(t['value']):,}" if t['value'] is not None else "—"
            price_str = f"${t['price']:,.2f}" if t['price'] is not None else "—"

            row_html = f'''
            <tr>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb;">
                    <span style="color: {color}; font-weight: 600;">{t['action']}</span>
                </td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; font-weight: 600;">{t['symbol']}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{t['shares']}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{price_str}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{val_str}</td>'''

            if is_single:
                score = t['lynch_score'] if show_lynch else t['buffett_score']
                score_str = f"{int(score)}" if score is not None else "—"
                row_html += f'\n                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{score_str}</td>'
            else:
                if show_lynch:
                    l_score = t['lynch_score']
                    l_score_str = f"{int(l_score)}" if l_score is not None else "—"
                    row_html += f'\n                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{l_score_str}</td>'
                if show_buffett:
                    b_score = t['buffett_score']
                    b_score_str = f"{int(b_score)}" if b_score is not None else "—"
                    row_html += f'\n                <td style="padding: 8px 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{b_score_str}</td>'

            row_html += '\n            </tr>'
            rows += row_html

        trades_html = f'''
        <h3 style="margin: 24px 0 12px; color: #18181b;">Trades</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background: #f4f4f5;">{header_html}
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>'''

    portfolio_value = _format_currency(briefing.get('portfolio_value'))
    portfolio_return = _format_pct(briefing.get('portfolio_return_pct'))
    spy_return = _format_pct(briefing.get('spy_return_pct'))
    alpha = _format_pct(briefing.get('alpha'))

    alpha_val = briefing.get('alpha', 0) or 0
    alpha_color = '#16a34a' if alpha_val >= 0 else '#dc2626'

    summary = briefing.get('executive_summary', '')
    summary_html = markdown.markdown(summary)

    return f'''
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0; color: #18181b;">
        <div style="background: #18181b; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 20px;">{portfolio_name}</h1>
            <p style="margin: 4px 0 0; opacity: 0.8; font-size: 14px;">Daily Strategy Briefing</p>
        </div>

        <div style="padding: 24px; background: white; border: 1px solid #e5e7eb; border-top: none;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                <tr>
                    <td style="width: 33.33%; padding-right: 8px;">
                        <div style="background: #f4f4f5; padding: 12px; border-radius: 6px; text-align: center;">
                            <div style="font-size: 12px; color: #71717a;">Portfolio Value</div>
                            <div style="font-size: 20px; font-weight: 700;">{portfolio_value}</div>
                        </div>
                    </td>
                    <td style="width: 33.33%; padding: 0 8px;">
                        <div style="background: #f4f4f5; padding: 12px; border-radius: 6px; text-align: center;">
                            <div style="font-size: 12px; color: #71717a;">Return</div>
                            <div style="font-size: 20px; font-weight: 700;">{portfolio_return}</div>
                        </div>
                    </td>
                    <td style="width: 33.33%; padding-left: 8px;">
                        <div style="background: #f4f4f5; padding: 12px; border-radius: 6px; text-align: center;">
                            <div style="font-size: 12px; color: #71717a;">Alpha vs SPY</div>
                            <div style="font-size: 20px; font-weight: 700; color: {alpha_color};">{alpha}</div>
                        </div>
                    </td>
                </tr>
            </table>

            <h3 style="margin: 0 0 12px; color: #18181b;">Summary</h3>
            <div style="font-size: 14px; line-height: 1.6; color: #374151;">
                <p style="margin: 0 0 12px;">{summary_html}</p>
            </div>

            {trades_html}

            <div style="margin-top: 24px; text-align: center;">
                <a href="{APP_URL}/portfolios" style="display: inline-block; background: #18181b; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: 600;">
                    View Full Details
                </a>
            </div>
        </div>

        <div style="padding: 16px 24px; text-align: center; font-size: 12px; color: #a1a1aa;">
            <p>SPY Return: {spy_return} &bull; {briefing.get('trades_executed', 0)} trades executed</p>
        </div>
    </div>'''


def send_briefing_email(to_email: str, briefing: dict, portfolio_name: str) -> bool:
    """Send a strategy briefing email via Resend."""
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        logger.warning("RESEND_API_KEY not set. Skipping briefing email.")
        return False

    resend.api_key = api_key
    html_content = build_briefing_html(briefing, portfolio_name)

    try:
        r = resend.Emails.send({
            "from": "Papertree AI <info@papertree.ai>",
            "to": to_email,
            "subject": f"Daily Briefing: {portfolio_name}",
            "html": html_content
        })
        logger.info(f"Briefing email sent to {to_email}. ID: {r.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send briefing email to {to_email}: {e}")
        return False
