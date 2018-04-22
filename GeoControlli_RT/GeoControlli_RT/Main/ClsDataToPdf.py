# thanks to: https://github.com/jcalazan/data-to-pdf/blob/master/data_to_pdf.py
# attention: MODIFIED FOR SPECIFIC USE !
#
#from operator import itemgetter

from reportlab.lib import colors
from reportlab.lib.colors import black #,red,blue
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm #,inch
from reportlab.lib.pagesizes import A4, portrait #, letter, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, Image, SimpleDocTemplate, Spacer, PageBreak, Indenter #, BaseDocTemplate, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER #, TA_RIGHT

class ClsDataToPdf():
    """
    Export a list of dictionaries to a table in a PDF file.
    """
    
    def __init__(self, lst_intest, lst_rif_dati, lst_info_sess, fields, data, lst_num_ctrl, out_if_ok=True, descr_out=True, logo=None, intestaz=None): #title=None,
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
        self.fields = fields
        self.data = data
#        self.title = title
        self.file_logo=logo
        self.file_intestaz=intestaz
        self.lst_intest=lst_intest
        self.lst_rif_dati=lst_rif_dati
        self.lst_info_sess=lst_info_sess
        self.lst_num_ctrl=lst_num_ctrl
        self.out_if_ok=out_if_ok
        self.descr_out=descr_out
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
 
        #stile_sottot=ParagraphStyle('Sottotitolo',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=18,spaceBefore=20,spaceAfter=10,leftIndent=0,alignment=TA_CENTER,textColor=black)
        stile_intest=ParagraphStyle('Intestazione',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=12,spaceBefore=8,spaceAfter=0,leftIndent=0,alignment=TA_CENTER,textColor=colors.darkgrey)
        stile_catego=ParagraphStyle('Categoria',parent=styles['Normal'],fontName='LiberationSansBold',fontSize=18,spaceBefore=20,spaceAfter=10,leftIndent=20,alignment=TA_LEFT,textColor=black)
        stile_gruppo=ParagraphStyle('Gruppo',parent=styles['Normal'],fontName='LiberationSansBoldItalic',fontSize=14,spaceBefore=12,spaceAfter=10,leftIndent=40,alignment=TA_LEFT,textColor=black)
        stile_err_ok=ParagraphStyle('Esito_err_ok',parent=styles['Normal'],fontName='LiberationSans',fontSize=10,spaceBefore=2,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkgreen)
        stile_err_dc=ParagraphStyle('Esito_err_desc',parent=styles['Normal'],fontName='LiberationSans',fontSize=10,spaceBefore=2,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkred)
        stile_err_id=ParagraphStyle('Esito_err_id',parent=styles['Normal'],fontName='LiberationSansItalic',fontSize=10,spaceBefore=1,spaceAfter=0,leftIndent=80,alignment=TA_LEFT,textColor=colors.darkred)
        stile_descri=ParagraphStyle('Descriz_ctrl',parent=styles['Normal'],fontName='LiberationSansItalic',fontSize=10,spaceBefore=1,spaceAfter=0,leftIndent=60,alignment=TA_LEFT,textColor=colors.darkgrey)
        
        story = []
        
        id_file_img=None
          
        if self.file_logo:
            path_to_file=self.file_logo
            #id_file_img = open(path_to_file, 'rb')
            ##img=Image(f,width=37.8*mm,height=13.9*mm)
            #img=Image(id_file_img)
            img=Image(path_to_file)
            fatt_larg=img.drawWidth/img.drawHeight
            img.drawHeight=20.0*mm
            img.drawWidth=20.0*mm*fatt_larg
            img.hAlign='CENTER' #RIGHT
            story.append( img )
            #id_file_img.close()
#           story.append(Spacer(width=0, height=5*mm))

        if self.file_intestaz:
            path_to_file=self.file_intestaz
            f = open(path_to_file, 'r')
            linee_intest=f.readlines()
            story.append(Spacer(width=0, height=3*mm))
            for linea in linee_intest:
                story.append(Paragraph(linea, stile_intest))
            f.close()
          
#       if self.title:
#           story.append(Paragraph(self.title, styleH))
#           story.append(Spacer(width=0, height=2*mm))
             
        story.append(Spacer(width=0, height=15*mm))
             
        for intest in self.lst_intest:
            story.append(Indenter(left=intest['INDENT_MM']*mm, right=0*mm))
            story.append(Paragraph(intest['TESTO'], styles[intest['STILE']]))
            story.append(Spacer(width=0*mm, height=intest['BELOW_MM']*mm))
            story.append(Indenter(left=-intest['INDENT_MM']*mm, right=0*mm))

        story.append(Spacer(width=0*mm, height=10*mm))
             
        for rif_dati in self.lst_rif_dati:
            story.append(Indenter(left=rif_dati['INDENT_MM']*mm, right=0*mm))
            story.append(Paragraph(rif_dati['TESTO'], styles[rif_dati['STILE']]))
            story.append(Spacer(width=0*mm, height=rif_dati['BELOW_MM']*mm))
            story.append(Indenter(left=-rif_dati['INDENT_MM']*mm, right=0*mm))

        story.append(Spacer(width=0*mm, height=10*mm))
             
        for info_sess in self.lst_info_sess:
            story.append(Indenter(left=info_sess['INDENT_MM']*mm, right=0*mm))
            story.append(Paragraph(info_sess['TESTO'], styles[info_sess['STILE']]))
            story.append(Spacer(width=0*mm, height=info_sess['BELOW_MM']*mm))
            story.append(Indenter(left=-info_sess['INDENT_MM']*mm, right=0*mm))

        story.append(Spacer(width=0*mm, height=10*mm))
        
        info_sess=self.lst_info_sess[0] # per usare la stessa indentazione
        story.append(Indenter(left=info_sess['INDENT_MM']*mm, right=0*mm))
        str_out='Numero controlli previsti: '+str(self.lst_num_ctrl[0])
        story.append(Paragraph(str_out, styles[info_sess['STILE']]))
        str_out='Numero controlli eseguiti: '+str(self.lst_num_ctrl[1])
        story.append(Paragraph(str_out, styles[info_sess['STILE']]))
        story.append(Indenter(left=-info_sess['INDENT_MM']*mm, right=0*mm))
 
        story.append(PageBreak())
             
#         converted_data = self.__convert_data()
#         table = Table(converted_data, hAlign=table_halign)
#         table.setStyle(TableStyle([
#             ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#             ('ALIGN',(0, 0),(0,-1), data_align),
#             ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.black),
#             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
#         ]))
#         story.append(table)
#          
#         story.append(Spacer(width=0*mm, height=10*mm))
#          
#         prova=[('Esito',),['pippo'],['pluto'],['paperino']]
#         table=Table(prova, hAlign='CENTER')
#         table.setStyle(TableStyle([
#             ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#             ('ALIGN',(0, 0),(0,-1), data_align),
#             ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.red),
#             ('BOX', (0,0), (-1,-1), 0.25, colors.green),
#             ('TEXTCOLOR', (0, 0), (-1,-1), colors.blue)
#         ]))
#         story.append(table)
#  
#         story.append(PageBreak()) 
   
        row2=self.data[0]
        
        lista_codmod_out=[]
        
        is_res_ok=False
        if row2['ESITO_CTRL'].upper()=='OK': is_res_ok=True
        
        descr_mod_pulita=self.togli_var_sign(row2['DES_MOD'])
        descr_mod_pulita += ' (vedi modello '
        descr_mod_pulita += row2['COD_MOD']
        descr_mod_pulita += ')'
        
        #story.append(Spacer(width=0*mm, height=5*mm))
        #story.append(Indenter(left=0*mm, right=0*mm))
        story.append(Paragraph(row2['DES_CAT'], stile_catego))
        #story.append(Spacer(width=0*mm, height=3*mm))
        #story.append(Indenter(left=2*mm, right=0*mm))
        #story.append(Paragraph('<font color="blue">' + row2['DES_GRP']+'</font>', stileGrp))
        story.append(Paragraph(row2['DES_GRP'], stile_gruppo))
        #story.append(Indenter(left=-2*mm, right=0*mm))
        #story.append(Spacer(width=0*mm, height=2*mm))
        #story.append(Indenter(left=4*mm, right=0*mm))
        if row2['DB_STATO']!=0:
            story.append(Paragraph('errore in '+row2['DES_CTRL']+': '+row2['DB_MSG_ERR'], stile_err_dc))
        else:
            if is_res_ok: #(row2['ESITO_CTRL'].upper()=='OK')
                if self.out_if_ok:
                    if self.descr_out: story.append(Paragraph(descr_mod_pulita, stile_descri))
                    story.append(Paragraph(row2['DES_CTRL'] + ': ' + row2['ESITO_CTRL'], stile_err_ok))
            else:
                if self.descr_out: story.append(Paragraph(descr_mod_pulita, stile_descri))
                story.append(Paragraph(row2['DES_CTRL'], stile_err_dc))
                #story.append(Indenter(left=-4*mm, right=0*mm))
                #if not is_res_ok: #(row2['ESITO_CTRL'].upper()!='OK')
                #    #story.append(Indenter(left=6*mm, right=0*mm))
                #    #story.append(Paragraph(row2['ESITO_CTRL'], styles['Heading4']))
                #    #story.append(Paragraph('<font face="times" color="red" size=10>' + ' ' + row2['ESITO_CTRL'] + ' ' + '</font>', styles['Normal']))
                #    story.append(Paragraph(row2['ESITO_CTRL'], stile_err_id))
                #    #story.append(Indenter(left=-6*mm, right=0*mm))
                story.append(Paragraph(row2['ESITO_CTRL'], stile_err_id))
            lista_codmod_out=[row2['COD_MOD']]
         
        for row1, row2 in zip(self.data, self.data[1:]):
            descr_mod_pulita=self.togli_var_sign(row2['DES_MOD'])
            descr_mod_pulita += ' (vedi modello '
            descr_mod_pulita += row2['COD_MOD']
            descr_mod_pulita += ')'
            
            if(row1['DES_CAT'] != row2['DES_CAT']) : 
                #story.append(Spacer(width=0*mm, height=5*mm))
                #story.append(Indenter(left=0*mm, right=0*mm))
                story.append(Paragraph(row2['DES_CAT'], stile_catego))
                lista_codmod_out=[]
            if(row1['DES_GRP'] != row2['DES_GRP']) : 
                #story.append(Spacer(width=0*mm, height=3*mm))
                #story.append(Indenter(left=2*mm, right=0*mm))
                story.append(Paragraph(row2['DES_GRP'], stile_gruppo))
                #story.append(Indenter(left=-2*mm, right=0*mm))
                #story.append(Spacer(width=0*mm, height=2*mm))
                lista_codmod_out=[]
            
            if row2['DB_STATO']!=0:
                story.append(Paragraph('errore in '+row2['DES_CTRL']+': '+row2['DB_MSG_ERR'], stile_err_dc))
            else:
                is_res_ok=False
                if row2['ESITO_CTRL'].upper()=='OK': is_res_ok=True
            
                if(row1['DES_CTRL'] != row2['DES_CTRL']) : 
                    #story.append(Indenter(left=4*mm, right=0*mm))
                    if is_res_ok: #(row2['ESITO_CTRL'].upper()=='OK')
                        if self.out_if_ok:
                            if self.descr_out and row2['COD_MOD'] not in lista_codmod_out: #row1['COD_MOD']!=row2['COD_MOD']
                                story.append(Paragraph(descr_mod_pulita, stile_descri))
                                lista_codmod_out.append(row2['COD_MOD'])
                            story.append(Paragraph(row2['DES_CTRL'] + ': ' + row2['ESITO_CTRL'], stile_err_ok))
                    else:
                        if self.descr_out and row2['COD_MOD'] not in lista_codmod_out: #row1['COD_MOD']!=row2['COD_MOD']
                            story.append(Paragraph(descr_mod_pulita, stile_descri))
                            lista_codmod_out.append(row2['COD_MOD'])
                        story.append(Paragraph(row2['DES_CTRL'], stile_err_dc))
                        max_err=row2['MAX_ERR']
                        num_err=row2['NUM_ERR']
                        if (num_err>=max_err):
                            wng_out='***** ATTENZIONE: raggiunto il limite di '+str(max_err)+' segnalazioni'
                            story.append(Paragraph(wng_out, stile_err_dc))
                    #story.append(Indenter(left=-4*mm, right=0*mm))
                
                if not is_res_ok: #(row2['ESITO_CTRL'].upper()!='OK') 
                    #story.append(Indenter(left=6*mm, right=0*mm))
                    #story.append(Paragraph('<font face="times" color="red" size=8>' + ' ' + row2['ESITO_CTRL'] + ' ' + '</font>', styles['Normal']))
                    story.append(Paragraph(row2['ESITO_CTRL'], stile_err_id))
                    #story.append(Indenter(left=-6*mm, right=0*mm))
        
        doc.build(story, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)

#         if self.file_logo:
#             if id_file_img:
#                 id_file_img.close()

    def __convert_data(self):
        """
        Convert the list of dictionaries to a list of list to create
        the PDF table.
        """
        # Create 2 separate lists in the same order: one for the 
        # list of keys and the other for the names to display in the
        # table header.
        keys, names = zip(*[[k, n] for k, n in self.fields])
        new_data = [names]
        
        for d in self.data:
            new_data.append([d[k] for k in keys])
            
        return new_data
    
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
    
    def togli_var_sign(self, str_con_variab):
        str_pulita=str_con_variab
        for i in range(0,99):
            i=i+1
            str_pulita=str_pulita.replace(" $LAYER"+str(i)+"$", "")
            str_pulita=str_pulita.replace("$LAYER"+str(i)+"$", "")
            str_pulita=str_pulita.replace(".$ATTR"+str(i)+"$", "")
            str_pulita=str_pulita.replace("$ATTR"+str(i)+"$", "")
            str_pulita=str_pulita.replace(".$GEOM"+str(i)+"$", "")
            str_pulita=str_pulita.replace("$GEOM"+str(i)+"$", "")
            str_pulita=str_pulita.replace("$VALORI"+str(i)+"$", "")
        return str_pulita
