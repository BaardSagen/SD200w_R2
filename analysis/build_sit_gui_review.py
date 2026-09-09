"""Index screenshots and live menu snapshots from the SIT GUI review."""
from pathlib import Path
import json, hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'analysis/runtime_test/sit_live_review'
DOC=ROOT/'sd200DOc/SIT_GUI_GJENNOMGANG.md'

def read(name):
 return json.loads((OUT/name).read_text(encoding='utf-8'))
def link(path,label):
 p=Path(path)
 return f'[{label}](../{p.relative_to(ROOT).as_posix()})'
def usable(path):
 if not path or not Path(path).is_file():return False
 with Image.open(path) as im:
  return max(hi for lo,hi in im.convert('RGB').getextrema())>20
def picture(row):
 for key in ('screen_image','image'):
  if usable(row.get(key)):return row[key]
 return None
def tree(items,indent=0):
 result=[]
 for item in items:
  label=item['text'].replace('&','')
  if not label:continue
  result.append('  '*indent+label)
  result.extend(tree(item['children'],indent+1))
 return result
def flat(items,path=''):
 result={}
 for item in items:
  label=item['text'].replace('&','')
  name=(path+' > ' if path else '')+label
  if item['children']:result.update(flat(item['children'],name))
  elif label:result[item['id']]=name
 return result

startup=read('start_1788985839559484500.json')
legacy=read('click_1788986054119812400.json')
logger=read('button_1788986355372504600.json')
names=flat(startup['menus'])
exe=ROOT/'SAIV_Instrument_Terminal_v1.4.3_Sept2026.exe'
sha=hashlib.sha256(exe.read_bytes()).hexdigest()
parts=['# SIT – gjennomgang av kjørende program, 9. september 2026','',
'SIT 1.4.3 ble startet på det interaktive Windows-skrivebordet fra en byteidentisk kopi av leveransen. Menyer og dialoger ble faktisk åpnet. Denne rapporten bygger på skjermbilder, vindustilstand og menytre fra den kjørende prosessen, ikke bare prosjektbeskrivelser.','',
f'EXE: `{exe.name}`. SHA-256: `{sha}`.','',
'Dette er et undersøkelsesgrunnlag for en tro gjenskaping. Ingen ny Studio-utgave er bygget i denne gjennomgangen.','',
'## Hva den kjørende utgaven viser','',
'- Hovedvinduet har File, View, Display, Util og Help, en kompakt ikonlinje på blå bakgrunn og statuslinje nederst. Terminalen opptar hovedflaten.','- Terminalen har en fast blå knapperekke til høyre: Detect, Download, Convert, Merge, Interval, TIME/DATE, Print, Save text og Setup.','- Vanlige lister, standardtabeller og parvise grafer bruker hovedvinduet. Multigraph er et eget vindu med kanalvalg, skalaer, trykk/tid og visningsvalg.','- Setup har seks faner: Serial port, CU901 files, Modem, e-mail, Options og Calc values.','- Convert bruker en feltvis veiviser. Resultatet åpnes i et separat loggervindu med tabell, tidskurve, Export all fields og Import to SD2.','- Menyinnhold og tilgjengelighet endres med instrument-/datatype. Klassisk SD2 og importerte loggerdata må undersøkes hver for seg.','',
'## Faktisk gjennomført','',
'En kopi av data/test.SD2 med RF2/OP2 ble åpnet, måleutvalget bekreftet og de sju radene vist. Standardtabeller og tilgjengelige tid-/dybdegrafkommandoer ble åpnet. Eksportdialogene og verktøydialogene ble undersøkt. Multigraph ble åpnet med det gamle datasettet.','',
'Merge ble åpnet med data/2026_09_03_20-28-52_C.txt som master og data/saiv110 som søkemappe. Ved 0,0 sekunder viste den faktiske dialogen 79 masterrader, 12 skannede filer og fire treffiler. Ingen merge-utfil ble skrevet.','',
'Convert ble gjennomført med samme 79-raders loggerfil. Alle sju feltsteg (C, T, P, OF, Par, OxR og Tilt) ble åpnet med standardvalg. Resultatvinduet ble undersøkt. Import to SD2 opprettet logger_review.SD2 og følgefiler i gjennomgangens egen datamappe. Den importerte filen ble vist med SITs native Multigraph.','',
'Setup-fanene, hovedmenyene, eksport-/tabell-/grafundermenyene, About, Disclaimer, SMTP notice, manuell oppdateringsdialog og utskriftsdialog ble åpnet. Ingen utskriftsjobb eller oppdateringshenting ble startet.','',
'## Visuelle hovedreferanser','',
'| Tilstand | Bilde |','|---|---|']
keyshots=[
 ('Terminal ved oppstart','start_1788985839559484500.json',0),
 ('Klassisk SD2-liste','click_1788986054119812400.json',0),
 ('Parvis tidskurve','command_1788986062925542900.json',0),
 ('Standarddybdetabell (grunn dataserie gir ingen nivåtreff)','command_1788986056602351700.json',0),
 ('Klassisk Multigraph','button_1788986172347430000.json',0),
 ('Merge med faktisk søkeresultat','click_1788986244630183400.json',0),
 ('Loggerdata etter Convert','caption_1788986318435864700.json',0),
 ('Multigraph med importerte felt','button_1788986355372504600.json',0),
 ('About – direkte skjermbilde','command_1788986602854761800.json',0),
 ('Utskriftsdialog','command_1788986575691482000.json',0),
]
for label,name,i in keyshots:
 row=read(name)['windows'][i];p=picture(row)
 if p:parts.append(f'| {label} | {link(p,"Åpne bilde")} |')
parts+=['','## Setup og Convert, side for side','','| Side | Bilde |','|---|---|']
for label,name in [
 ('Setup / Serial port','click_1788985893256122800.json'),('Setup / CU901 files','mouse_1788985942713947900.json'),
 ('Setup / Modem','mouse_1788985944065659000.json'),('Setup / e-mail','mouse_1788985945342420800.json'),
 ('Setup / Options','mouse_1788985946620008500.json'),('Setup / Calc values','mouse_1788985947871916600.json'),
 ('Convert / C','command_1788986267109818400.json'),('Convert / T','click_1788986276301514200.json'),
 ('Convert / P','caption_1788986303657958200.json'),('Convert / OF','caption_1788986305015451100.json'),
 ('Convert / Par','caption_1788986306341798100.json'),('Convert / OxR','caption_1788986307688727100.json'),
 ('Convert / Tilt','caption_1788986309043604200.json')]:
 p=picture(read(name)['windows'][0])
 if p:parts.append(f'| {label} | {link(p,"Åpne bilde")} |')
parts+=['','## Åpnede menykommandoer','','Tabellen viser åpningsresponsen. Den er ikke dokumentasjon på at alle beregninger, eksportformater eller lagreoperasjoner er validert. En dialog som krever valg av fil ble undersøkt til filvalget; enkelte verktøy lukker det aktive datasettet og krever ny åpning.','','| Menykommando | Faktisk vist | Bevis |','|---|---|---|']
for path in sorted(OUT.glob('visit_command_*.json'),key=lambda p:int(p.stem.split('_')[-1])):
 command=int(path.stem.split('_')[-1]);summary=read(path.name);raw=json.loads(Path(summary['report']).read_text(encoding='utf-8'))
 rows=[r for r in raw['windows'] if r['cls'] not in ('TForm1','TApplication')]
 if not rows:rows=[r for r in raw['windows'] if r['cls']=='TForm1']
 labels=', '.join(r['title'] for r in rows) or 'Ingen ny dialog'
 shots=[link(picture(r),'Bilde') for r in rows if picture(r)]
 parts.append(f'| {names.get(command,str(command))} | {labels} | {", ".join(shots)} |')
parts+=['','## Komplett hovedmenytre ved oppstart','','Hentet fra den kjørende EXE-en, med undermenyene rekursivt. Tilgjengelighet er bevart i rå JSON-rapportene.','','```text',*tree(startup['menus']),'```','',
'## Menytilstand etter åpning av data','','Begge menytrær er lagret. Dette er observerte programtilstander, ikke en antakelse om at alle instrumenttyper har samme menyer.','','### Klassisk SD2','','```text',*tree(legacy['menus']),'```','','### Importerte loggerdata','','```text',*tree(logger['menus']),'```','',
'## Avgrensning og bildekvalitet','',
'Instrumentkommunikasjon, Detect-søk, Download, Interval, TIME/DATE og fysisk kalibrering er ikke utført i denne gjennomgangen. Det er heller ikke gjort en full numerisk validering eller prøvd alle kombinasjoner av enheter, datatyper og underdialoger. Disse må ikke merkes ferdigtestet ut fra skjermbilder.','',
'Bilder er tatt med PrintWindow og, der skrivebordstilgangen tillot det, direkte skjermfangst. PrintWindow kan mangle innhold fra egendegnede kontroller og vise andre vindusrammer enn skjermen. About er derfor også kontrollert med direkte skjermfangst. Svarte fangster inngår ikke som visuelle bevis i denne indeksen.','',
'Originalleveransene og originaldataene er beholdt. Gjennomgangen brukte egne testfiler under analysis/runtime_test/sit_live_review/data. Den ordinære EXE-en kan oppdatere sine vanlige brukerinnstillinger (for eksempel sist brukt filmappe og bekreftede Convert-valg); dette var ikke en isolert registertest.','',
'## Konsekvens for saiv-studio','',
'Neste implementering må bruke disse konkrete vinduene og arbeidsflytene som fasit. Studios fem toppsider, generelle grafvisning og samlede Utilities-side gjenskaper ikke SITs organisering. Visuell likhet alene gir heller ikke fil- eller beregningslikhet; dette må kontrolleres separat mot SIT. Ingen nye GSW-/TEOS-10-resultater må presenteres som identiske med de originale SIT-beregningene uten sammenligning.','',
'Rå bilder, fullstendige vindus-/kontrollrapporter og datasett ligger i analysis/runtime_test/sit_live_review. Inspeksjonsverktøy: analysis/inspect_sit_live.py. Denne indeksen genereres av analysis/build_sit_gui_review.py.','']
DOC.write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps(dict(report=str(DOC),menu_entries=len(names),visited_commands=len(list(OUT.glob('visit_command_*.json'))),exe_sha256=sha),indent=2))
