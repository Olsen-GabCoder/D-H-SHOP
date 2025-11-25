"""
Service de génération de factures PDF
Utilise ReportLab pour créer des factures professionnelles
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class PDFService:
    """
    Service centralisé pour la génération de PDF
    """
    
    @staticmethod
    def generate_invoice_pdf(order):
        """
        Génère une facture PDF professionnelle pour une commande
        
        Args:
            order: Instance du modèle Order
            
        Returns:
            BytesIO: Buffer contenant le PDF généré
        """
        try:
            # Créer un buffer en mémoire
            buffer = BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Container pour les éléments du PDF
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Style personnalisé pour le titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Style pour les informations
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12
            )
            
            # Style pour les totaux
            total_style = ParagraphStyle(
                'TotalStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#1f2937'),
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold'
            )
            
            # ==========================================
            # EN-TÊTE : Logo et informations boutique
            # ==========================================
            
            # Logo (si existe)
            logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo.png')
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=4*cm, height=2*cm)
                    elements.append(logo)
                    elements.append(Spacer(1, 0.5*cm))
                except Exception as e:
                    logger.warning(f'Impossible de charger le logo: {str(e)}')
            
            # Titre de la facture
            elements.append(Paragraph("FACTURE", title_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # Informations de la boutique et de la commande
            info_data = [
                ['<b>Informations Boutique</b>', '<b>Informations Commande</b>'],
                [
                    f'<b>{settings.SITE_NAME or "Ma Boutique"}</b><br/>'
                    f'{getattr(settings, "COMPANY_ADDRESS", "Adresse de la boutique")}<br/>'
                    f'Tél: {getattr(settings, "COMPANY_PHONE", "+228 XX XX XX XX")}<br/>'
                    f'Email: {getattr(settings, "COMPANY_EMAIL", settings.DEFAULT_FROM_EMAIL)}',
                    
                    f'<b>Numéro:</b> {order.order_number}<br/>'
                    f'<b>Date:</b> {order.created_at.strftime("%d/%m/%Y à %H:%M")}<br/>'
                    f'<b>Statut:</b> {order.get_status_display()}<br/>'
                    f'<b>Paiement:</b> {order.get_payment_status_display()}'
                ]
            ]
            
            info_table = Table(info_data, colWidths=[8*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))
            
            # ==========================================
            # INFORMATIONS CLIENT
            # ==========================================
            
            client_title = Paragraph('<b>FACTURER À:</b>', info_style)
            elements.append(client_title)
            
            client_info = f"""
            <b>{order.customer.user.get_full_name()}</b><br/>
            {order.shipping_address.address_line1}<br/>
            {order.shipping_address.address_line2 + '<br/>' if order.shipping_address.address_line2 else ''}
            {order.shipping_address.city}, {order.shipping_address.state or ''} {order.shipping_address.postal_code or ''}<br/>
            {order.shipping_address.country}<br/>
            Tél: {order.customer_phone}<br/>
            Email: {order.customer_email}
            """
            
            client_paragraph = Paragraph(client_info, info_style)
            elements.append(client_paragraph)
            elements.append(Spacer(1, 1*cm))
            
            # ==========================================
            # TABLEAU DES ARTICLES
            # ==========================================
            
            # En-tête du tableau
            table_data = [
                ['Article', 'Variante', 'Prix unitaire', 'Quantité', 'Total']
            ]
            
            # Lignes des articles
            for item in order.items.all():
                table_data.append([
                    item.product_name,
                    item.variant_details or '-',
                    f'{item.unit_price:.0f} FCFA',
                    str(item.quantity),
                    f'{item.subtotal:.0f} FCFA'
                ])
            
            # Créer le tableau
            items_table = Table(
                table_data,
                colWidths=[6*cm, 3*cm, 3*cm, 2*cm, 3*cm]
            )
            
            items_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Corps du tableau
                ('ALIGN', (0, 1), (1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                
                # Alternance de couleurs pour les lignes
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 1*cm))
            
            # ==========================================
            # TOTAUX
            # ==========================================
            
            totals_data = [
                ['', '', '', 'Sous-total:', f'{order.subtotal:.0f} FCFA'],
                ['', '', '', 'Livraison:', f'{order.shipping_cost:.0f} FCFA'],
            ]
            
            # Ajouter la taxe si elle existe
            if order.tax_amount > 0:
                totals_data.append(['', '', '', 'Taxes:', f'{order.tax_amount:.0f} FCFA'])
            
            # Ajouter la réduction si elle existe
            if order.discount_amount > 0:
                totals_data.append(['', '', '', 'Réduction:', f'-{order.discount_amount:.0f} FCFA'])
            
            # Total final
            totals_data.append(['', '', '', '<b>TOTAL:</b>', f'<b>{order.total:.0f} FCFA</b>'])
            
            totals_table = Table(
                totals_data,
                colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 4*cm]
            )
            
            totals_table.setStyle(TableStyle([
                ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (3, 0), (3, -2), 'Helvetica'),
                ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (3, 0), (-1, -2), 10),
                ('FONTSIZE', (3, -1), (-1, -1), 12),
                ('TEXTCOLOR', (3, -1), (-1, -1), colors.HexColor('#2563eb')),
                ('TOPPADDING', (3, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (3, 0), (-1, -1), 6),
                ('LINEABOVE', (3, -1), (-1, -1), 2, colors.HexColor('#2563eb')),
            ]))
            
            elements.append(totals_table)
            elements.append(Spacer(1, 1.5*cm))
            
            # ==========================================
            # NOTES ET INFORMATIONS ADDITIONNELLES
            # ==========================================
            
            if order.customer_notes:
                notes_style = ParagraphStyle(
                    'NotesStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6b7280')
                )
                elements.append(Paragraph('<b>Notes du client:</b>', notes_style))
                elements.append(Paragraph(order.customer_notes, notes_style))
                elements.append(Spacer(1, 0.5*cm))
            
            # Informations de livraison
            if order.shipping_zone:
                delivery_info = f"""
                <b>Informations de livraison:</b><br/>
                Zone: {order.shipping_zone.name}<br/>
                Type: {order.get_delivery_type_display()}<br/>
                Délai: {order.shipping_zone.get_delivery_days_display(order.delivery_type)}
                """
                
                delivery_style = ParagraphStyle(
                    'DeliveryStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6b7280')
                )
                
                elements.append(Paragraph(delivery_info, delivery_style))
                elements.append(Spacer(1, 1*cm))
            
            # Pied de page
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#9ca3af'),
                alignment=TA_CENTER
            )
            
            footer_text = f"""
            <b>Merci pour votre commande !</b><br/>
            Pour toute question, contactez-nous: {getattr(settings, 'COMPANY_EMAIL', settings.DEFAULT_FROM_EMAIL)}<br/>
            {getattr(settings, 'COMPANY_PHONE', '+228 XX XX XX XX')}
            """
            
            elements.append(Paragraph(footer_text, footer_style))
            
            # ==========================================
            # CONSTRUIRE LE PDF
            # ==========================================
            
            doc.build(elements)
            
            # Récupérer le contenu du buffer
            buffer.seek(0)
            
            logger.info(f'Facture PDF générée avec succès pour commande {order.order_number}')
            
            return buffer
            
        except Exception as e:
            logger.error(f'Erreur génération PDF pour commande {order.order_number}: {str(e)}')
            raise
    
    
    @staticmethod
    def generate_packing_slip_pdf(order):
        """
        Génère un bon de livraison PDF pour une commande
        (Version simplifiée sans prix)
        
        Args:
            order: Instance du modèle Order
            
        Returns:
            BytesIO: Buffer contenant le PDF généré
        """
        try:
            buffer = BytesIO()
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Titre
            elements.append(Paragraph("BON DE LIVRAISON", title_style))
            elements.append(Spacer(1, 1*cm))
            
            # Informations commande
            info_data = [
                ['<b>Numéro de commande:</b>', order.order_number],
                ['<b>Date:</b>', order.created_at.strftime("%d/%m/%Y")],
                ['<b>Client:</b>', order.customer.user.get_full_name()],
            ]
            
            info_table = Table(info_data, colWidths=[5*cm, 11*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))
            
            # Adresse de livraison
            elements.append(Paragraph('<b>LIVRER À:</b>', styles['Normal']))
            elements.append(Spacer(1, 0.3*cm))
            
            address_info = f"""
            {order.shipping_address.full_name}<br/>
            {order.shipping_address.address_line1}<br/>
            {order.shipping_address.address_line2 + '<br/>' if order.shipping_address.address_line2 else ''}
            {order.shipping_address.city}, {order.shipping_address.postal_code or ''}<br/>
            Tél: {order.shipping_address.phone}
            """
            
            elements.append(Paragraph(address_info, styles['Normal']))
            elements.append(Spacer(1, 1*cm))
            
            # Liste des articles (sans prix)
            table_data = [['Article', 'Variante', 'Quantité']]
            
            for item in order.items.all():
                table_data.append([
                    item.product_name,
                    item.variant_details or '-',
                    str(item.quantity)
                ])
            
            items_table = Table(table_data, colWidths=[10*cm, 4*cm, 3*cm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 2*cm))
            
            # Signature
            signature_data = [
                ['Signature du livreur:', 'Signature du client:'],
                ['', ''],
                ['', ''],
            ]
            
            signature_table = Table(signature_data, colWidths=[8*cm, 8*cm], rowHeights=[0.8*cm, 2*cm, 0.8*cm])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
            ]))
            
            elements.append(signature_table)
            
            doc.build(elements)
            buffer.seek(0)
            
            logger.info(f'Bon de livraison PDF généré pour commande {order.order_number}')
            
            return buffer
            
        except Exception as e:
            logger.error(f'Erreur génération bon de livraison pour {order.order_number}: {str(e)}')
            raise