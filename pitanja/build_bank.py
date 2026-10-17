import re,glob,json,sys,collections
Q=[];err=[];k='?';src=''
for f in sorted(glob.glob('pitanja/*.txt')):
  src=f.split('/')[-1][:2]
  for n,l in enumerate(open(f,encoding='utf-8'),1):
    l=l.strip()
    if not l: continue
    if l.startswith('# K:'): k=l[4:].strip(); continue
    try:
      body,e=l.split(' || ',1)
      t,rest=body.split('| ',1)
      parts=[p.strip() for p in rest.split(' | ')]
      q={'t':t,'k':k,'e':e.strip()}
      if t in('S','M'):
        q['q']=parts[0]; opts=parts[1:]
        q['o']=[o.lstrip('*') for o in opts]; q['c']=[i for i,o in enumerate(opts) if o.startswith('*')]
        assert len(q['o'])>=3
        if t=='S': assert len(q['c'])==1
        else: assert len(q['c'])>=2 and len(q['c'])<len(q['o'])
      elif t=='T':
        q['q']=parts[0]; assert parts[1] in('T','N'); q['a']=parts[1]=='T'
      elif t=='P':
        q['q']=parts[0]; pr=[x.split(' = ',1) for x in parts[1].split(' ; ')]
        assert all(len(x)==2 for x in pr) and len(pr)>=2; q['p']=[[a.strip(),b.strip()] for a,b in pr]
      elif t=='R':
        q['q']=parts[0]; q['i']=[x.strip() for x in parts[1].split(' > ')]; assert len(q['i'])>=3
      elif t=='F':
        txt=rest; gaps=re.findall(r'\[([^\]]+)\]',txt); assert gaps
        q['q']=re.sub(r'\[[^\]]+\]','{}',txt); q['b']=[g.split('/') for g in gaps]
        assert all(len(g)>=2 for g in q['b'])
      else: raise Exception('type')
      q['id']=src+'-'+str(n); Q.append(q)
    except Exception as ex: err.append((f,n,l[:80],repr(ex)))
print(len(Q),'pitanja; greske:',len(err))
for x in err: print(x)
print(collections.Counter(q['t'] for q in Q))
print(collections.Counter(q['k'] for q in Q))
json.dump(Q,open('bank.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
# --- izvedena pitanja (grupirana s izvornim, u ispitu najviše jedno po grupi)
import random; random.seed(3)
D=[]
for q in Q:
  q['g']=q['id']
  if q['t']=='P' and len(q['p'])>=3:
    rights=[b for a,b in q['p']]
    for j,(a,b) in enumerate(q['p']):
      wrong=[r for r in rights if r!=b]
      if j%2==0:
        D.append({'t':'T','k':q['k'],'q':'Je li ovo spajanje točno? »'+a+'« → '+b,'a':True,'e':q['e'],'id':q['id']+'d'+str(j),'g':q['id']})
      elif wrong:
        D.append({'t':'T','k':q['k'],'q':'Je li ovo spajanje točno? »'+a+'« → '+random.choice(wrong),'a':False,'e':'Točno je: »'+a+'« → '+b+'. '+q['e'],'id':q['id']+'d'+str(j),'g':q['id']})
  if q['t']=='R':
    it=q['i']
    for j in range(0,len(it)-1,2):
      x,y=it[j],it[j+1]
      D.append({'t':'S','k':q['k'],'q':'Redoslijed – što dolazi prije? (iz niza: '+q['q'].rstrip('.')+')','o':[x,y],'c':[0],'e':'Ispravan niz: '+' → '.join(it)+'. '+q['e'],'id':q['id']+'r'+str(j),'g':q['id']})
for q in Q: q.pop('g',None)
for q in Q: q['g']=q['id']
Q2=Q+D
print('izvedeno',len(D),'ukupno',len(Q2))
json.dump(Q2,open('bank.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
