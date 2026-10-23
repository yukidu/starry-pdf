import { useRef, useState } from 'react';

type Tool = 'merge' | 'split' | 'rotate' | 'optimize';
const TOOLS: { id: Tool; label: string; desc: string; icon: string }[] = [
  { id:'merge', label:'合併 PDF', desc:'多個 PDF 合成一個檔案', icon:'▣' },
  { id:'split', label:'拆分 PDF', desc:'依頁碼分成單頁檔案', icon:'✂' },
  { id:'rotate', label:'旋轉 PDF', desc:'整份旋轉 90、180、270 度', icon:'↻' },
  { id:'optimize', label:'內容壓縮', desc:'最佳化 PDF 內容，不保證每份都會變小', icon:'⇥' },
];
const MAX_FILE_BYTES=12*1024*1024;
const MAX_FILES=6;

function errorMessage(body: unknown): string {
 if (typeof body==='object' && body!==null && 'detail' in body && typeof body.detail==='string') return body.detail;
 return '處理失敗，請稍後重試。';
}
function validate(files:File[],tool:Tool):string|null {
 const min=tool==='merge'?2:1, max=tool==='merge'?MAX_FILES:1;
 if(files.length<min||files.length>max) return tool==='merge'?'請上傳 2～6 個 PDF。':'請選擇 1 個 PDF。';
 if(files.some(file=>!file.name.toLowerCase().endsWith('.pdf'))) return '只支援 PDF 檔案。';
 if(files.some(file=>file.size>MAX_FILE_BYTES)) return '每個檔案不可超過 12 MB。';
 return null;
}
export default function App(){
 const [tool,setTool]=useState<Tool>('merge');
 const [files,setFiles]=useState<File[]>([]);
 const [pages,setPages]=useState('1-3');
 const [degrees,setDegrees]=useState('90');
 const [processing,setProcessing]=useState(false);
 const [message,setMessage]=useState('');
 const [error,setError]=useState(false);
 const filePicker=useRef<HTMLInputElement>(null);
 const current=TOOLS.find(x=>x.id===tool)!;
 function switchTool(next:Tool){
   if(processing)return;
   setTool(next);setFiles([]);setMessage('');
   if(filePicker.current)filePicker.current.value='';
 }
 function choose(next:FileList|null){
   if(processing||!next)return;
   const chosen=Array.from(next);setFiles(chosen);
   const issue=validate(chosen,tool);setError(Boolean(issue));setMessage(issue??'');
 }
 async function process(){
   const issue=validate(files,tool);
   if(issue){setError(true);setMessage(issue);return;}
   setProcessing(true);setError(false);setMessage('正在處理你的 PDF，請勿關閉此頁…');
   try{
     const form=new FormData();
     if(tool==='merge')files.forEach(file=>form.append('files',file));
     else form.append('file',files[0]);
     if(tool==='split')form.append('pages',pages);
     if(tool==='rotate')form.append('degrees',degrees);
     const response=await fetch(`/api/pdf/${tool}`,{method:'POST',body:form,credentials:'same-origin',cache:'no-store'});
     if(!response.ok){
       const payload:unknown=await response.json().catch(()=>undefined);
       throw new Error(errorMessage(payload));
     }
     const blob=await response.blob();
     const contentType=response.headers.get('content-type')||'';
     if(!contentType.includes(tool==='split'?'application/zip':'application/pdf'))throw new Error('伺服器回傳的檔案類型不正確。');
     const url=URL.createObjectURL(blob);
     const anchor=document.createElement('a');
     anchor.href=url;anchor.download=tool==='split'?'繁星-PDF-拆分.zip':`繁星-PDF-${current.label.replaceAll(' ','-')}.pdf`;
     document.body.append(anchor);anchor.click();anchor.remove();
     window.setTimeout(()=>URL.revokeObjectURL(url),5000);
     setMessage('已完成！檔案已送到你的下載資料夾。');
   }catch(caught){
     setError(true);setMessage(caught instanceof Error?caught.message:'處理發生錯誤。');
   }finally{setProcessing(false);}
 }
 return <div className="app">
  <header className="masthead">
    <div className="brand"><span className="brand-icon">✦</span><div><strong>繁星 PDF</strong><small>Starry PDF · 文件工作台</small></div></div>
    <span className="version">開發預覽 v0.2</span>
  </header>
  <main>
    <section className="intro"><span className="eyebrow">DOC STUDIO</span><h1>你的 PDF，<br/><span>輕鬆整理。</span></h1><p>在手機與電腦處理文件。無廣告、不保存檔案，處理完成就直接下載。</p></section>
    <section className="workspace" aria-label="PDF 工具">
      <div className="section-title"><h2>選擇 PDF 工具</h2><small>首批開放 4 項工具</small></div>
      <div className="tool-grid">{TOOLS.map(item=><button key={item.id} type="button" aria-pressed={tool===item.id} onClick={()=>switchTool(item.id)} disabled={processing} className={`tool-card ${tool===item.id?'active':''}`}>
        <span className="tool-symbol">{item.icon}</span><strong>{item.label}</strong><small>{item.desc}</small>
      </button>)}</div>
      <div className="upload-panel">
        <div className="section-title"><h2>{current.label}</h2><small>{tool==='merge'?'最多 6 個檔案':'一次一個檔案'}</small></div>
        <div className="drop-zone" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();choose(e.dataTransfer.files);}}>
          <span className="upload-icon">⇧</span><strong>將 PDF 拖曳到這裡</strong><span>或從裝置選擇檔案，每個最多 12 MB</span>
          <input ref={filePicker} className="sr-only" type="file" accept=".pdf,application/pdf" multiple={tool==='merge'} onChange={e=>choose(e.target.files)} disabled={processing}/>
          <button type="button" className="pick" onClick={()=>filePicker.current?.click()} disabled={processing}>選擇 PDF 檔案</button>
        </div>
        {files.length>0&&<div className="files"><strong>已選檔案（{files.length}）</strong>{files.map((f,i)=><p key={`${f.name}-${i}`}>📄 {f.name} <span>{(f.size/(1024*1024)).toFixed(2)} MB</span></p>)}</div>}
        {tool==='split'&&<label className="field">要拆分的頁碼<span>例如：1-3,5（會輸出 ZIP）</span><input value={pages} onChange={e=>setPages(e.target.value)} maxLength={240} disabled={processing} placeholder="1-3,5"/></label>}
        {tool==='rotate'&&<label className="field">旋轉角度<select value={degrees} onChange={e=>setDegrees(e.target.value)} disabled={processing}><option value="90">順時針 90°</option><option value="180">旋轉 180°</option><option value="270">順時針 270°</option></select></label>}
        <button className="process" type="button" onClick={process} disabled={processing}>{processing?'正在處理…':`開始${current.label}`}</button>
        {message&&<div className={`notice ${error?'error':'ok'}`} role="status">{message}</div>}
        <p className="footnote">文件只在此次處理期間使用，不建立個人檔案庫。正式上線前仍需新增外部登入保護。</p>
      </div>
    </section>
  </main><footer>✦ Starry PDF · 以開源技術建立 · 目前為本機開發預覽</footer>
 </div>;
}
