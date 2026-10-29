import zipfile
import os

src_path = '/Users/devdhapodkar/Downloads/AI Plag_srushti Kale (1).docx'
target_name = '24070521505_AI_Plag_Dev_Dilip_Dhapodkar.docx'

with zipfile.ZipFile(src_path, 'r') as zin:
    file_map = {item.filename: zin.read(item.filename) for item in zin.infolist()}

doc_xml = file_map['word/document.xml'].decode('utf-8')

replacements = [
    ('<w:t>Srushti.Kale</w:t>', '<w:t>Dev.Dhapodkar</w:t>'),
    ('<w:t>23070521067_srushti</w:t>', '<w:t>24070521505_Dev Dilip</w:t>'),
    ('<w:t>Kale.pdf</w:t>', '<w:t>Dhapodkar.docx</w:t>'),
    ('<w:t>3078</w:t>', '<w:t>2371</w:t>'),
    ('<w:t>15,618</w:t>', '<w:t>15,582</w:t>'),
    ('<w:t>1.9</w:t>', '<w:t>2.5</w:t>'),
    ('<w:t>17,</w:t>', '<w:t>29,</w:t>'),
    ('<w:t>1:3074638943</w:t>', '<w:t>1:3074812954</w:t>')
]

for old, new in replacements:
    count = doc_xml.count(old)
    doc_xml = doc_xml.replace(old, new)
    print(f"Replaced '{old}' -> '{new}': {count} occurrences")

file_map['word/document.xml'] = doc_xml.encode('utf-8')

# Write out the updated docx files
for out_path in [
    target_name,
    'AI Plag_Dev Dhapodkar.docx',
    '24070521505_Dev_Dilip_Dhapodkar_AI_Plag.docx'
]:
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for fname, data in file_map.items():
            zout.writestr(fname, data)
    print(f"Successfully saved {out_path} ({os.path.getsize(out_path):,} bytes)")

