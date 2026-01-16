import csv
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse, JsonResponse
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Circle, Line, Polygon
from reportlab.graphics import renderPDF
from openpyxl import Workbook
from .models import Hero, Region, Skill
from django.core.serializers.json import DjangoJSONEncoder
import json


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(Region)
class RegionAdmin(BaseAdmin):
    list_display = ('name', 'environment_type', 'hero_count')
    search_fields = ('name',)

    def hero_count(self, obj):
        return obj.heroes.count()
    hero_count.short_description = 'Nombre de Héros'


@admin.register(Skill)
class SkillAdmin(BaseAdmin):
    list_display = ('name', 'damage_type', 'mana_cost')
    list_filter = ('damage_type',)
    search_fields = ('name',)


def export_to_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields if field.name != 'id']
    field_names.extend(['region', 'skills'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = []
        for field in meta.fields:
            if field.name != 'id':
                val = getattr(obj, field.name)
                if hasattr(val, 'id'):
                    val = str(val)
                row.append(val)
        row.append(str(obj.region) if obj.region else '')
        row.append(', '.join([s.name for s in obj.skills.all()]))
        writer.writerow(row)

    return response


export_to_csv.short_description = 'Exporter en CSV'


def export_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Héros'

    headers = ['Surnom', 'Classe', 'Niveau', 'HP Actuel', 'XP', 'Or', 'Actif', 'Région', 'Compétences']
    ws.append(headers)

    for hero in queryset:
        skills_list = ', '.join([s.name for s in hero.skills.all()])
        ws.append([
            hero.nickname,
            hero.get_job_class_display(),
            hero.level,
            hero.hp_current,
            hero.xp,
            hero.gold,
            'Oui' if hero.is_active else 'Non',
            str(hero.region) if hero.region else '',
            skills_list
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=heroes.xlsx'
    wb.save(response)

    return response


export_to_excel.short_description = 'Exporter en Excel'


def generate_character_sheet(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, 'Selectionnez exactement un heros.', level='error')
        return

    hero = queryset.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=fiche_{hero.nickname}.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []

    # Palette de couleurs
    COLOR_HEADER = colors.HexColor('#1a1a2e')
    COLOR_ACCENT = colors.HexColor('#f4c430')
    COLOR_BG = colors.HexColor('#f5f5f5')
    COLOR_TEXT = colors.HexColor('#333333')
    COLOR_SKILL_PHY = colors.HexColor('#e74c3c')
    COLOR_SKILL_MAG = colors.HexColor('#9b59b6')
    COLOR_SKILL_HEAL = colors.HexColor('#27ae60')
    COLOR_SKILL_MIX = colors.HexColor('#f39c12')

    # === TITRE PRINCIPAL ===
    title_style = ParagraphStyle(
        'HeroTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=COLOR_HEADER,
        alignment=1,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph('FICHE PERSONNAGE', title_style))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontSize=16,
        textColor=COLOR_ACCENT,
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica'
    )
    story.append(Paragraph('PAFFMMO RPG ATLAS', subtitle_style))

    # Ligne de separation
    line_table = Table([['']], colWidths=[450])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))

    # === NOM ET NIVEAU ===
    name_style = ParagraphStyle(
        'HeroName',
        fontSize=22,
        textColor=COLOR_HEADER,
        alignment=1,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(hero.nickname, name_style))

    class_style = ParagraphStyle(
        'ClassInfo',
        fontSize=14,
        textColor=COLOR_TEXT,
        alignment=1,
        spaceAfter=40,
        fontName='Helvetica'
    )
    story.append(Paragraph(f'Niveau {hero.level} - {hero.get_job_class_display()}', class_style))
    story.append(Spacer(1, 20))

    # === TABLEAU DES STATS ===
    stats_title = ParagraphStyle(
        'StatsTitle',
        fontSize=12,
        textColor=COLOR_HEADER,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=8
    )
    story.append(Paragraph('STATISTIQUES', stats_title))

    # En-tetes du tableau
    header_data = [['Attribut', 'Valeur', 'Attribut', 'Valeur']]
    header_table = Table(header_data, colWidths=[120, 130, 120, 130])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_ACCENT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ]))
    story.append(header_table)

    # Donnees du tableau
    stats_data = [
        ['HP Actuel', f'{hero.hp_current}', 'HP Maximum', f'{hero.max_hp}'],
        ['Experience (XP)', f'{hero.xp}', 'Niveau', f'{hero.level}'],
        ['Or', f'{hero.gold}', 'Actif', 'Oui' if hero.is_active else 'Non'],
        ['Region', hero.region.name if hero.region else 'Inconnue', 'Cree le', hero.created_at.strftime('%d/%m/%Y')],
    ]
    stats_table = Table(stats_data, colWidths=[120, 130, 120, 130])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [COLOR_BG, colors.HexColor('#e8e8e8')]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 15))

    # === BARRE DE HP ===
    hp_pct = hero.hp_current / hero.max_hp
    hp_color = colors.HexColor('#27ae60') if hp_pct > 0.5 else colors.HexColor('#f39c12') if hp_pct > 0.25 else colors.HexColor('#e74c3c')

    hp_table = Table([['']], colWidths=[int(400 * hp_pct)])
    hp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), hp_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    hp_title = ParagraphStyle(
        'HPTitle',
        fontSize=12,
        textColor=COLOR_HEADER,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=5
    )
    story.append(Paragraph('BARRE DE VIE', hp_title))
    story.append(hp_table)

    hp_text_style = ParagraphStyle(
        'HPText',
        fontSize=11,
        textColor=COLOR_TEXT,
        alignment=1,
        spaceAfter=15
    )
    story.append(Paragraph(f'{hero.hp_current} / {hero.max_hp} HP ({hp_pct*100:.1f}%)', hp_text_style))

    # === COMPETENCES ===
    if hero.skills.exists():
        skill_title = ParagraphStyle(
            'SkillTitle',
            fontSize=12,
            textColor=COLOR_HEADER,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=10
        )
        story.append(Paragraph('COMPETENCES', skill_title))

        for skill in hero.skills.all():
            dmg_color = {
                'physical': COLOR_SKILL_PHY,
                'magical': COLOR_SKILL_MAG,
                'healing': COLOR_SKILL_HEAL,
                'mixed': COLOR_SKILL_MIX,
            }.get(skill.damage_type, colors.grey)

            skill_text = f'{skill.name} - {skill.get_damage_type_display()} ({skill.mana_cost} mana)'
            skill_style = ParagraphStyle(
                'SkillItem',
                fontSize=11,
                textColor=dmg_color,
                spaceBefore=3,
                spaceAfter=3,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(skill_text, skill_style))

            sub_style = ParagraphStyle(
                'SkillSub',
                fontSize=10,
                textColor=colors.grey,
                spaceBefore=0,
                spaceAfter=5,
                fontName='Helvetica'
            )
            story.append(Paragraph(f'Type: {skill.get_damage_type_display()} | Cout en mana: {skill.mana_cost}', sub_style))

        story.append(Spacer(1, 10))

    # === BIOGRAPHIE ===
    if hero.biography:
        bio_title = ParagraphStyle(
            'BioTitle',
            fontSize=12,
            textColor=COLOR_HEADER,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=10
        )
        story.append(Paragraph('BIOGRAPHIE', bio_title))

        bio_style = ParagraphStyle(
            'BioText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=4,
            spaceBefore=5,
            textColor=COLOR_TEXT
        )
        story.append(Paragraph(hero.biography, bio_style))
        story.append(Spacer(1, 15))

    # === FOOTER ===
    story.append(Spacer(1, 10))
    line_table2 = Table([['']], colWidths=[450])
    line_table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(line_table2)

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,
        spaceBefore=15,
    )
    story.append(Paragraph(f'Fiche genere le {hero.created_at.strftime("%d/%m/%Y a %H:%M")} - PAFFMMO RPG ATLAS', footer_style))

    doc.build(story)
    return response


generate_character_sheet.short_description = 'Générer la fiche PDF'


def dashboard_view(modeladmin, request, queryset=None):
    heroes = Hero.objects.all()

    job_classes = {}
    for hero in heroes:
        job_classes[hero.get_job_class_display()] = job_classes.get(hero.get_job_class_display(), 0) + 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.pie(job_classes.values(), labels=job_classes.keys(), autopct='%1.1f%%', startangle=90)
    ax1.set_title('Répartition des Classes')

    region_levels = {}
    for hero in heroes:
        region_name = str(hero.region) if hero.region else 'Sans région'
        if region_name not in region_levels:
            region_levels[region_name] = []
        region_levels[region_name].append(hero.level)

    avg_levels = {k: sum(v) / len(v) for k, v in region_levels.items()}
    ax2.bar(avg_levels.keys(), avg_levels.values(), color='steelblue')
    ax2.set_title('Moyenne des Niveaux par Région')
    ax2.set_xlabel('Région')
    ax2.set_ylabel('Niveau Moyen')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')
    plt.close()

    return response


dashboard_view.short_description = 'Graphiques'


@admin.register(Hero)
class HeroAdmin(BaseAdmin):
    list_display = ('nickname', 'job_class', 'level', 'hp_current', 'region', 'is_active', 'created_at')
    list_filter = ('job_class', 'is_active', 'region', 'created_at')
    search_fields = ('nickname', 'biography')
    filter_horizontal = ('skills',)
    actions = [export_to_csv, export_to_excel, generate_character_sheet]

    def get_actions(self, request):
        actions = super().get_actions(request)
        return actions

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['show_dashboard'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        heroes = Hero.objects.all()

        job_classes = {}
        for hero in heroes:
            display = hero.get_job_class_display()
            job_classes[display] = job_classes.get(display, 0) + 1

        region_levels = {}
        for hero in heroes:
            region_name = str(hero.region) if hero.region else 'Sans région'
            if region_name not in region_levels:
                region_levels[region_name] = []
            region_levels[region_name].append(hero.level)

        avg_levels = {k: sum(v) / len(v) for k, v in region_levels.items()}

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        ax1.pie(job_classes.values(), labels=job_classes.keys(), autopct='%1.1f%%', startangle=90)
        ax1.set_title('Répartition des Classes')

        ax2.bar(avg_levels.keys(), avg_levels.values(), color='steelblue')
        ax2.set_title('Moyenne des Niveaux par Région')
        ax2.set_xlabel('Région')
        ax2.set_ylabel('Niveau Moyen')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        import base64
        from io import BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        context = {
            'title': 'Dashboard PAFFMMO',
            'image_base64': image_base64,
            'hero_count': heroes.count(),
            'avg_level': sum([h.level for h in heroes]) / len(heroes) if heroes else 0,
            'total_gold': sum([h.gold for h in heroes]),
        }

        return TemplateResponse(request, 'admin/dashboard.html', context)