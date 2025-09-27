import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import xlsxwriter
from datetime import datetime

class MdGenerator:
    def generate(self, test_plan):
        md = f"# {test_plan['title']}\n\n"
        md += f"**Generated:** {test_plan.get('generated_date', 'N/A')}\n"
        md += f"**Target Device:** {test_plan.get('target_device', 'N/A')}\n\n"
        
        md += "## Overview\n"
        md += f"{test_plan.get('overview', '')}\n\n"
        
        md += "## Test Procedures\n\n"
        for i, step in enumerate(test_plan['test_steps'], 1):
            md += f"### Step {i}: {step['title']}\n"
            md += f"**Type:** {step['type']}\n"
            md += f"**Description:** {step['description']}\n"
            if 'expected_result' in step: md += f"**Expected Result:** {step['expected_result']}\n"
            if 'test_points' in step: md += f"**Test Points:** {', '.join(step['test_points'])}\n"
            if 'equipment' in step: md += f"**Equipment:** {', '.join(step['equipment'])}\n"
            md += "\n---\n\n"
        
class PDFGenerator:
    def generate(self, test_plan):
        filename = f"output/{test_plan['title'].replace(' ', '_')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30
        )
        story.append(Paragraph(test_plan['title'], title_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Overview", styles['Heading2']))
        story.append(Paragraph(test_plan.get('overview', ''), styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Test Procedures", styles['Heading2']))
        
        for i, step in enumerate(test_plan['test_steps'], 1):
            step_title = f"Step {i}: {step['title']}"
            story.append(Paragraph(step_title, styles['Heading3']))
            
            data = [
                ['Type:', step.get('type', 'N/A')],
                ['Description:', step.get('description', 'N/A')],
                ['Expected Result:', step.get('expected_result', 'N/A')],
                ['Test Points:', ', '.join(step.get('test_points', []))],
                ['Equipment:', ', '.join(step.get('equipment', []))]
            ]
            
            table = Table(data, colWidths=[1.5*inch, 4.5*inch])
            story.append(table)
            story.append(Spacer(1, 12))
        
        doc.build(story)
        return filename


class ExcelGenerator:
    def generate(self, test_plan):
        filename = f"output/{test_plan['title'].replace(' ', '_')}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        
        summary_ws = workbook.add_worksheet('Test Summary')
        checklist_ws = workbook.add_worksheet('Test Checklist')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFFF',
            'font_color': 'white'
        })
        
        summary_ws.write(0,0, 'Test Plan Summary', header_format)
        summary_ws.write(0,2, 'Title:', workbook.add_format({'bold': True}))
        summary_ws.write(1,2, test_plan['title'])
        summary_ws.write(1,3, 'Total Steps:', workbook.add_format({'bold': True}))
        summary_ws.write(2,3, len(test_plan['test_steps']))
        
        headers = ['Step', 'Title', 'Type', 'Description', 'Expected Result', 'Pass/Fail', 'Notes']
        for col, header in enumerate(headers):
            checklist_ws.write(0, col, header, header_format)
        
        for i, step in enumerate(test_plan['test_steps'], 1):
            checklist_ws.write(i, 0, i)
            checklist_ws.write(i, 1, step.get('title', ''))
            checklist_ws.write(i, 2, step.get('type', ''))
            checklist_ws.write(i, 3, step.get('description', ''))
            checklist_ws.write(i, 4, step.get('expected_result', ''))
            checklist_ws.write(i, 5, '')
            checklist_ws.write(i, 6, '')
        
        workbook.close()
        return filename

class JSONGenerator:
    def generate(self, test_plan):
        # Add metadata
        test_plan['metadata'] = {
            'generated_by': 'Aeronix AI Test Generator',
            'generated_at': datetime.now().isoformat(),
            'version': '1.0',
            'format': 'json'
        }
        
        # Structure for API consumption
        structured_output = {
            'test_plan': test_plan,
            'statistics': {
                'total_steps': len(test_plan['test_steps']),
                'test_types': self._count_test_types(test_plan['test_steps']),
                'estimated_duration': self._estimate_duration(test_plan['test_steps'])
            }
        }
        
        return json.dumps(structured_output, indent=4)
    
    def _count_test_types(self, test_steps):
        types = {}
        for step in test_steps:
            test_type = step.get('type', 'Unknown')
            types[test_type] = types.get(test_type, 0) + 1
        return types
    
    def _estimate_duration(self, test_steps):
        # CHANGE LATER
        time_estimates = {
            'Power Test': 15,
            'RF Test': 30,
            'Digital Test': 10,
            'Protocol Test': 20,
            'Environmental Test': 60
        }
        
        total_minutes = 0
        for step in test_steps:
            test_type = step.get('type', 'Digital Test')
            total_minutes += time_estimates.get(test_type, 15)
        
        return f"{total_minutes} minutes"

def format_output(test_plan, formats=["markdown", "pdf", "json"]):
    outputs = {}
    for format_type in formats:
        if format_type == "markdown":
            outputs['markdown'] = MdGenerator().generate(test_plan)
        elif format_type == "pdf":
            outputs['pdf'] = PDFGenerator().generate(test_plan)
        elif format_type == "json":
            outputs['json'] = JSONGenerator().generate(test_plan)
        elif format_type == "excel":
            outputs['excel'] = ExcelGenerator().generate(test_plan)
    
    return outputs