from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from reportlab.platypus import ListFlowable, ListItem

from NextSteps.models import CountryUserPref, DisciplineUserPref, LevelUserPref, User
from NextSteps.models import ProgramUserPref, InsttUserPref, InstituteProgramSeats
from NextSteps.models import StudentCategory, StudentCategoryUserPref
from NextSteps.models import InstituteEntranceExam, InstituteSurveyRanking
from NextSteps.models import InstituteJEERanks, InstituteCutOffs, InstituteAdmRoutes


PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()
styleH5 = styles["Heading5"]
styleH4 = styles["Heading4"]
styleH3 = styles["Heading3"]
styleH2 = styles["Heading2"]
styleH1 = styles["Heading1"]

style = styles["Normal"]
pageinfo = "Generated by: NextSteps.co.in"
usernm = ''

def consRepFirstPage(canvas, doc):

    Title = "Information on Preferred Institutes"
    canvas.saveState()
    canvas.setFont("Helvetica", 16)
    canvas.line(0, PAGE_HEIGHT-128, PAGE_WIDTH, PAGE_HEIGHT-128)

    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
#    canvas.drawString(PAGE_WIDTH/2.0, PAGE_HEIGHT-128, 'for ' + usernm)
    
    canvas.setFont("Helvetica", 9)
    canvas.drawString(inch, 0.75 * inch, "First Page                                                                                                                     / %s" % pageinfo)
#    canvas.drawRightString(inch, 0.75 * inch, "Created by: NextSteps")
    canvas.setFont("Helvetica", 14)
    canvas.restoreState()    
    
def consRepLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d                                                                                                                     / %s" % (doc.page, pageinfo))
    canvas.setFont("Helvetica", 14)
    canvas.restoreState()    


def buildConsRep(response, request):
    doc = SimpleDocTemplate(response)
    Story = [Spacer(1,2*inch)]

    # Get user name
    usernm = request.user.username

    # Get user id
    userid = User.objects.filter(username = request.user).values('id')

    # Get user student category
    catList = StudentCategoryUserPref.objects.filter(User_id__in = userid)[:1]
    stuCatId = ""
    stuCatDesc = ""
                
    for s in catList:
        studentCatList = StudentCategory.objects.filter(category = s.StudentCategory_id)[:1]
        for c in studentCatList:
            stuCatId = c.category
            stuCatDesc = c.description

    # Preferences section header
    preftext = ("Your preferences")
    p = Paragraph(preftext, styleH2)
    Story.append(p)
    Story.append(Spacer(1,0.2*inch))
    
    
    # Let's get the preferences
    programUserList = ProgramUserPref.objects.filter(User__in=userid).values(
        "Program_id"). order_by('Program__description')

    insttNameUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name').order_by('Institute__instt_name').distinct()
    
    
    insttUserList = InsttUserPref.objects.filter(User__in=userid).values('Institute__instt_code',
        'Institute__instt_name','Institute__address_1', 'Institute__address_2',
        'Institute__address_3','Institute__city', 'Institute__state', 'Institute__pin_code',
        'Institute__phone_number','Institute__email_id','Institute__website',
        'Institute__InstituteType_id').order_by(
            'Institute__Country', 'Institute__city', 'Institute__instt_name').distinct()

    insttUserProgList = InsttUserPref.objects.filter(User__in=userid).values(
        'Institute__instt_code', 'Program_id').distinct()

    
    p = Paragraph("Programs:", styleH5)
    Story.append(p)

    for p in programUserList:
        para = Paragraph(p["Program_id"], styleH5)
        l = ListFlowable([para], bulletType='bullet', start='diamond')
        Story.append(l)

    Story.append(Spacer(1,0.2*inch))
    p = Paragraph("Institutes:", styleH5)
    Story.append(p)

    for i in insttNameUserList:
        para = Paragraph(i["Institute__instt_name"], styleH5)
        l = ListFlowable([para], bulletType='bullet', start='diamond')
        Story.append(l)

    Story.append(Spacer(1,0.2*inch))
        
    p = Paragraph("Student Category:", styleH5)
    Story.append(p)
    
    p = Paragraph(stuCatId + "("+stuCatDesc + ")", styleH5)
    Story.append(p)

    Story.append(PageBreak())


    # Let's display the institute Details
    p = Paragraph("Details:", styleH2)
    Story.append(p)
    Story.append(Spacer(1,0.2*inch))

    

    for il in insttUserList:
        
        p = Paragraph("<font name=Courier-Bold color=blue size=14><b><i>" + il["Institute__instt_name"] + "</i></b></font>", styleH2)
        Story.append(p)
        l = HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.blue, spaceBefore=1, spaceAfter=1, hAlign='LEFT', vAlign='BOTTOM', dash=None)
        Story.append(l)

        # email Id can be null, so handling it first
        if il["Institute__email_id"]:
            emailid = il["Institute__email_id"]
        else:
            emailid = "N/A"
            
        addr = Paragraph(
                il["Institute__address_1"] + " " + il["Institute__address_2"] + "<br />" 
                + il["Institute__address_3"] + " " + il["Institute__city"] + il["Institute__state"] + " " + str(il["Institute__pin_code"]) + "<br />" 
                + "Phone: " + " Email: " + emailid + " Website: " + il["Institute__website"]
                , style)
        Story.append(addr)
        Story.append(Spacer(1,0.1*inch))
                
        year = "2017"
        # Get Institute survey Ranking
        insttRank = InstituteSurveyRanking.objects.filter(year = year, Institute_id = il["Institute__instt_code"])

        if insttRank.exists():
            for r in insttRank:
                rank = r.rank
            p = Paragraph("<font name=Courier-Bold size=10> Survey Rank : #" + str(rank) + "</font>", style)
            Story.append(p)

        prg = Paragraph("<i>" + "My Preferred Programs Offered here:" + "</i>", styleH4)
        Story.append(prg)
        Story.append(Spacer(1,0.2*inch))

        for ip in insttUserProgList:

            
            if il["Institute__instt_code"] == ip["Institute__instt_code"] :
                
                
                
                progDetailsTxt = "<b>" + ip["Program_id"] + "</b>"
                
                # Get seats for the student category and current program 
                progSeats = InstituteProgramSeats.objects.filter(
                    Institute_id=il["Institute__instt_code"], Program_id=ip["Program_id"], 
                    StudentCategory_id=stuCatId)
                progDetailsTxt =  progDetailsTxt + "<br /><font name=Courier-Bold size=10><b>Number of Seats:</b></font> " 
                if progSeats.exists():
                    for ps in progSeats:
                        if ps.number_of_seats > 0:
                            progDetailsTxt =  progDetailsTxt + " <font name=Courier size=10>" + str(ps.number_of_seats) + " (" + ps.quota + " quota) </font>"
                        else:
                            progDetailsTxt =  progDetailsTxt + "<font name=Courier size=10> *N/A<font>"            
                else:
                    progDetailsTxt =  progDetailsTxt + "<font name=Courier size=10> *N/A</font>"            
                
                
                # Get Eetrance Exam Details
                entExam = InstituteEntranceExam.objects.filter(
                    Institute_id=il["Institute__instt_code"]).values('EntranceExam__entrance_exam_code',
                        'EntranceExam__description')
                if entExam.exists():
                    progDetailsTxt = progDetailsTxt + "<br /><font name=Courier-Bold size=10><b>Entrance Exam:</b></font><br /> " 
                    for ee in entExam:
                        progDetailsTxt = progDetailsTxt + ">>&nbsp;&nbsp;&nbsp;&nbsp;<font name=Courier size=10>" + ee["EntranceExam__description"] + "</font> <br />"
                    
                year = "2017"

                # Get the JEE opening-closing ranks
                insttJEERanks = InstituteJEERanks.objects.filter(year=year, Institute_id=il["Institute__instt_code"],
                                Program_id=ip["Program_id"], StudentCategory_id=stuCatId)

                year = "2017"

                if insttJEERanks.exists():
                    progDetailsTxt = progDetailsTxt + "<br /><font name=Courier-Bold size=10><b>" + year + " " + "JEE Opening and Closing Ranks:</b></font><br />" 
                    for ir in insttJEERanks:
                        progDetailsTxt = progDetailsTxt + ">>&nbsp;&nbsp;&nbsp;&nbsp;<font name=Courier size=10>" + ir.quota + " - Opening Rank: " + str(ir.opening_rank) + ", Closing Rank: " + str(ir.closing_rank) + "</font> <br />"
                
                # Get the cut Offs
                insttCutOffs = InstituteCutOffs.objects.filter(year=year, Institute_id=il["Institute__instt_code"],
                                Program_id=ip["Program_id"], StudentCategory_id=stuCatId)
                
                if insttCutOffs.exists():
                    progDetailsTxt = progDetailsTxt + "<br /><font name=Courier-Bold size=10><b>" + year + " " + "Cut Off:</b></font> <br />" 
                    for ic in insttCutOffs:
                        progDetailsTxt = progDetailsTxt + ">>&nbsp;&nbsp;&nbsp;&nbsp;<font name=Courier size=10>" + ic.quota + " " + ic.cutOff + "</font> <br />"

                # Get Admission Routes
                insttAdmRoutes = InstituteAdmRoutes.objects.filter(Institute_id=il["Institute__instt_code"])
                

                if insttAdmRoutes.exists():
                    progDetailsTxt = progDetailsTxt + "<br /><font name=Courier-Bold size=10><b>" "Admission Routes:</b></font> <br />" 
                    for ia in insttAdmRoutes:
                        progDetailsTxt = progDetailsTxt + ">>&nbsp;&nbsp;&nbsp;&nbsp;<font name=Courier size=10>" + ia.adm_route + " - " + ia.description + "</font> <br />"
                
                prog = Paragraph( progDetailsTxt, style)
                Story.append(prog)
                Story.append(Spacer(1,0.2*inch))
                
                
                
        Story.append(Spacer(1,0.5*inch))

    
    Story.append(Paragraph("__End of Report__", style))    
    l = HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.grey, spaceBefore=1, spaceAfter=1, hAlign='LEFT', vAlign='BOTTOM', dash=None)
    Story.append(l)

    disclaimerTxt = "<font name=Courier size=7>* Disclaimer: The information in this report is for your references only. While we do take all the care to ensure that information in our database is current and relevant, due to changes that can happen at any time or we may not have the information available at the time you are printing report, we may not have the current information. Hence we do not claim that all the information is accurate. It is advised that students/parents may seek information directly from the institute for the latest.</font>" 
    disclaimer = Paragraph(disclaimerTxt, style)
    Story.append(disclaimer)   

        
#        row = []
#        row.append(il["Institute__instt_name"] + "\n" + il["Institute__address_1"] + "," + str(il["Institute__phone_number"]) + " " + str(il["Institute__email_id"]) + " " + str(il["Institute__website"]))
#        data.append(row)
#    tbl=Table(data)
#    Story.append(tbl)
#    Story.append(Spacer(1,0.2*inch))



#programs = ListFlowable(programUserList)    
#    programs = ListFlowable([ListItem(Paragraph(x, style), leftIndent=35, bulletColor='black', value='circle') for x in programUserList], bulletType='bullet')
#    Story.append(programs)
#    Story.append(Spacer(1,0.2*inch))

    
    doc.build(Story, onFirstPage=consRepFirstPage, onLaterPages=consRepLaterPages)
    