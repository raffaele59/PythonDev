from reportlab.lib import colors
from reportlab.lib.colors import black #,red,blue
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm #,inch
from reportlab.lib.pagesizes import A4, portrait #, letter, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Image, SimpleDocTemplate, Spacer, PageBreak, Indenter #, BaseDocTemplate, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER #, TA_RIGHT

from PyQt4.QtGui import QMessageBox

class ClsModDocToPdf():
    """
    Export model documentation as PDF file.
    """
    
    def __init__(self, lst_intest, lst_doc_mod):
        """
        Arguments:
            fields - A tuple of tuples ((fieldname/key, display_name)) 
                specifying the fieldname/key and corresponding display
                name for the table header.
            data - The data to insert to the table formatted as a list of
                dictionaries.
            sort_by - A tuple (sort_key, sort_order) specifying which field
                to sort by and the sort order ('ASC', 'DESC').
            title - The title to display at the beginning of the document.
        """
        self.lst_intest=lst_intest
        self.lst_doc_mod=lst_doc_mod

        self.formato=portrait(A4) #letter #landscape(A4)
        self.leftMrg=15*mm
        self.rightMrg=15*mm
        self.topMrg=15*mm
        self.bottomMrg=20*mm
#         self.sort_by = sort_by
        
    def export(self, filename, data_align='LEFT', table_halign='LEFT'):
        """
        Export the data to a PDF file.
        
        Arguments:
            filename - The filename for the generated PDF file.
            data_align - The alignment of the data inside the table (eg.
                'LEFT', 'CENTER', 'RIGHT')
            table_halign - Horizontal alignment of the table on the page
                (eg. 'LEFT', 'CENTER', 'RIGHT')
        """
        doc = SimpleDocTemplate(filename, pagesize=self.formato, leftMargin=self.leftMrg, rightMargin=self.rightMrg, topMargin=self.topMrg, bottomMargin=self.bottomMrg)
#        doc = BaseDocTemplate("C:/Users/Isr/git/MyDev/SpatialControls/Main/ReportTemplate.pdf",showBoundary=1,pagesize=landscape(letter))
        # for sample styleSheets http://eric.sau.pe/tag/reportlab-getsamplestylesheet/
        styles = getSampleStyleSheet()
#         styleH = styles['Heading1']
 
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        pdfmetrics.registerFont(TTFont('LiberationSans', 'LiberationSans-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('LiberationSansBold', 'LiberationSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('LiberationSansItalic', 'LiberationSans-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('LiberationSansBoldItalic', 'LiberationSans-BoldItalic.ttf'))
 
        ##stile_sottot=ParagraphStyle('Sottotitolo',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=18,spaceBefore=20,spaceAfter=10,leftIndent=0,alignment=TA_CENTER,textColor=black)
        #stile_intest=ParagraphStyle('Intestazione',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=12,spaceBefore=8,spaceAfter=0,leftIndent=0,alignment=TA_CENTER,textColor=colors.darkgrey)
        #stile_catego=ParagraphStyle('Categoria',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=18,spaceBefore=20,spaceAfter=10,leftIndent=20,alignment=TA_LEFT,textColor=black)
        #stile_gruppo=ParagraphStyle('Gruppo',parent=styles['Normal'],fontName='LiberationSansBoldItalic',fontSize=14,spaceBefore=12,spaceAfter=10,leftIndent=40,alignment=TA_LEFT,textColor=black)
        #stile_err_ok=ParagraphStyle('Esito_err_ok',parent=styles['Normal'],fontName='LiberationSans',fontSize=10,spaceBefore=2,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkgreen)
        #stile_err_dc=ParagraphStyle('Esito_err_desc',parent=styles['Normal'],fontName='LiberationSans',fontSize=10,spaceBefore=2,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkred)
        #stile_err_id=ParagraphStyle('Esito_err_id',parent=styles['Normal'],fontName='LiberationSansItalic',fontSize=10,spaceBefore=1,spaceAfter=0,leftIndent=80,alignment=TA_LEFT,textColor=colors.darkred)
        #stile_descri=ParagraphStyle('Descriz_ctrl',parent=styles['Normal'],fontName='LiberationSansItalic',fontSize=10,spaceBefore=1,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkgrey)
        stile_codmod=ParagraphStyle('cod_mod',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=16,spaceBefore=20,spaceAfter=15,leftIndent=0,alignment=TA_LEFT,textColor=black)
        stile_docmod=ParagraphStyle('doc_mod',parent=styles['Normal'],fontName='LiberationSans',fontSize=12,spaceBefore=4,spaceAfter=0,leftIndent=20,alignment=TA_LEFT,textColor=black)
        
        story = []
        
        for intest in self.lst_intest:
            story.append(Indenter(left=intest['INDENT_MM']*mm, right=0*mm))
            story.append(Paragraph(intest['TESTO'], styles[intest['STILE']]))
            story.append(Spacer(width=0*mm, height=intest['BELOW_MM']*mm))
            story.append(Indenter(left=-intest['INDENT_MM']*mm, right=0*mm))
# 
#         story.append(Spacer(width=0*mm, height=10*mm))
             
        for doc_mod in self.lst_doc_mod:
            story.append(Paragraph(doc_mod['COD_MOD'], stile_codmod))
            str_doc_mod=doc_mod['DOC_MOD']
            righe=str_doc_mod.split('\n')
            #QMessageBox.information(None, "doc_mod", str_doc_mod, QMessageBox.Ok, QMessageBox.NoButton)
            for riga in righe:
                story.append(Paragraph(riga, stile_docmod))

        #story.append(Spacer(width=0*mm, height=10*mm))
        
        doc.build(story, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)

    def addPageNumber(self, canvas, doc):
        """
        Add the page number
        """
        page_num = canvas.getPageNumber()
        page_text = "Pag. %s" % page_num
        # note: reportlab starts from the bottom-left
        width, height = self.formato # letter
        height=height # !wng

        canvas.drawRightString(width - 10 * mm, 10 * mm, page_text)
    