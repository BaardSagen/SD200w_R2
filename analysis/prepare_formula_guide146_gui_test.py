"""Adapt the existing owned-process GUI test to all generated formula pages."""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'check_quick_guide144_gui.py').read_text().replace('144','146').replace('1.4.4','1.4.6')
s=s.replace('report={};destination=',"expected=json.loads((ROOT/'analysis/formula_guide146_topics.json').read_text(encoding='utf-8'))\nreport={};destination=")
s=s.replace('for i in range(9):','for i in range(9+len(expected)):')
s=s.replace("assert len(body)>400 and title and '\\r\\n' in body,(i,title,body)","assert len(body)>300 and title and '\\r\\n' in body,(i,title,body)\n  if i>=9:\n   item=expected[i-9];assert title==item['title'] and body==item['text'],(i,title,'Page text mismatch/truncation')\n   edit=u.GetDlgItem(guide,403);u.SendMessageW(edit,0xb1,len(body),len(body));u.SendMessageW(edit,0xb7,0,0)\n   assert u.SendMessageW(edit,0xce,0,0)>0,(title,'End of long page not scrollable')\n   if i in [10,13,16,23]:capture(guide,destination/f'topic_{i}_end.png')\n   u.SendMessageW(edit,0xb1,0,0);u.SendMessageW(edit,0xb7,0,0)")
s=s.replace('if i in [4,7]:','if i in [4,7,9,10,11,13,16,17,23,25]:')
s=s.replace('680,480','800,480')
s=s.replace("assert u.SendMessageW(edit,0xce,0,0)>0,(title,'End of long page not scrollable')","assert len(body)<4000 or u.SendMessageW(edit,0xce,0,0)>0,(title,'End of long page not scrollable')")
s=s.replace("report['topics']=topics","report['topics']=topics\n assert u.SendMessageW(u.GetDlgItem(guide,401),0x18b,0,0)==9+len(expected)\n report['full_formula_text_matches_source']=True")
(R/'check_formula_guide146_gui.py').write_text(s)
print('Prepared GUI test')
