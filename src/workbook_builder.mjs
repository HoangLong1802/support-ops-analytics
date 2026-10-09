import fs from "node:fs/promises";
import {SpreadsheetFile, Workbook} from "@oai/artifact-tool";
const [inputPath,outputPath,previewDir]=process.argv.slice(2);
const spec=JSON.parse(await fs.readFile(inputPath,"utf8")), wb=Workbook.create(), locations=new Map();
function letter(n){let x="";for(n++;n;n=Math.floor((n-1)/26))x=String.fromCharCode(65+(n-1)%26)+x;return x;}
function fmt(n){
 if(["Date","Hire_Date"].includes(n))return "yyyy-mm-dd";
 if(["Period","Previous_Period"].includes(n))return "yyyy-mm";
 if(/Rate|Share|Compliance|Percentage|Utilization|Percent/.test(n))return "0.00%";
 if(/Hours|Minutes|FTE|Staffing_Gap|Average_CSAT|Average_Daily/.test(n))return "#,##0.00";
 return "#,##0";
}
for(const [name,tables] of Object.entries(spec.sections)){
 const s=wb.worksheets.add(name);s.showGridLines=false;
 s.getRange("A1").values=[[name==="README"?"Customer Support Operations":name.replaceAll("_"," ")]];
 s.getRange("A1").format.font={name:"Arial",size:16,bold:true,color:"#24445C"};
 s.getRange("A2").values=[["Dữ liệu mô phỏng. 01/10/2025–30/09/2026; snapshot 01/10/2026 00:00 UTC+7."]];
 s.getRange("A2").format.font={name:"Arial",size:10,color:"#536574"};s.getRange("A2").format.rowHeight=23;
 let row=3;const widths=[];
 for(let i=0;i<tables.length;i++){
  const {title,columns,rows}=tables[i];
  s.getRange("A"+row).values=[[title]];s.getRange("A"+row).format.font={name:"Arial",size:11,bold:true,color:"#24445C"};
  const first=row+1,last=first+rows.length;
  const cells=rows.map(r=>r.map((v,c)=>v!=null&&/^(Date|Hire_Date|Period|Previous_Period)$/.test(columns[c])?new Date(v):v));
  s.getRangeByIndexes(first-1,0,rows.length+1,columns.length).values=[columns,...cells];
  const rg=s.getRange("A"+first+":"+letter(columns.length-1)+last);
  rg.format.font={name:"Arial",size:11,color:"#172B3A"};rg.format.rowHeight=25;rg.format.verticalAlignment="center";
  const tab=s.tables.add(rg,true,name+"_T"+(i+1));tab.style="TableStyleMedium2";
  s.getRange("A"+first+":"+letter(columns.length-1)+first).format={fill:"#24445C",font:{name:"Arial",size:10,bold:true,color:"#FFFFFF"},wrapText:true,rowHeight:42,verticalAlignment:"center"};
  for(let c=0;c<columns.length;c++){
   const col=columns[c],L=letter(c);
   let width=/Definition|Contents|Business_Impact|Reason|Analytical_Impact|Recommended_Action/.test(col)?65:Math.min(31,Math.max(17,col.length+2));
  if(name==="Executive_KPIs")width=[38,22,78][c];
   if(name==="README")width=[35,24,38][c]||20;
   width=Math.max(widths[c]||0,width);widths[c]=width;
   s.getRange(L+first+":"+L+last).format.columnWidth=width;
   const body=s.getRange(L+(first+1)+":"+L+last);body.setNumberFormat(fmt(col));body.format.wrapText=true;
   for(let r=0;r<rows.length;r++){
    if(typeof rows[r][c]==="string"&&!/^(Date|Hire_Date|Period|Previous_Period)$/.test(col)){
     let lines=Math.ceil(rows[r][c].length/(width-3));
     if(lines>1)s.getRange("A"+(first+r+1)+":"+letter(columns.length-1)+(first+r+1)).format.rowHeight=Math.max(27,Math.min(360,lines*17));
    }
   }
  }
   for(let r=0;r<rows.length;r++){
   const lines=Math.max(1,...rows[r].map((v,c)=>typeof v==="string"&&!/^(Date|Hire_Date|Period|Previous_Period)$/.test(columns[c])?Math.ceil(v.length/Math.max(10,widths[c]-3)):1));
   s.getRange("A"+(first+r+1)+":"+letter(columns.length-1)+(first+r+1)).format.rowHeight=Math.max(25,Math.min(360,lines*18));
  }
  if(name==="Executive_KPIs"||(name==="README"&&i===0))for(let r=0;r<rows.length;r++){
   let label=String(rows[r][0]),nf=/%/.test(label)?"0.00%":!label.startsWith("Backlog")&&/Hours|Minutes|Average CSAT|Average Arrivals|Weekday/.test(label)?"#,##0.00":"#,##0";
   s.getRange("B"+(first+r+1)).setNumberFormat(nf);
  }
  locations.set(name+"|"+title,{s,first,last,columns});
  if(i===0)s.freezePanes.freezeRows(first);
  row=last+3;if(name==="README"&&i===0)row=23;
 }
}
function chart(sheet,title,ct,category,value,type,start,end,limit){
 const l=locations.get(sheet+"|"+title),last=limit?l.first+limit:l.last;
 const c=l.s.charts.add(type,[l.s.getRange(letter(l.columns.indexOf(category))+l.first+":"+letter(l.columns.indexOf(category))+last),l.s.getRange(letter(l.columns.indexOf(value))+l.first+":"+letter(l.columns.indexOf(value))+last)]);
 c.title=ct;c.hasLegend=false;c.titleTextStyle.typeface="Arial";c.titleTextStyle.fontSize=14;
 c.xAxis={axisType:"textAxis",textStyle:{typeface:"Arial",fontSize:11}};
 c.yAxis={numberFormatCode:/Rate|Compliance|Utilization/.test(value)?"0%":"#,##0",numberFormatSourceLinked:false,textStyle:{typeface:"Arial",fontSize:11}};
 c.series.items[0].fill="#397C9C";c.setPosition(start,end);
}
chart("README","SLA compliance","SLA compliance tại snapshot","Stage","Compliance_Rate","bar","F4","L18");
chart("Demand_Analysis","Monthly ticket trend","Monthly ticket arrivals","Month","Ticket_Count","line","I3","P18");
chart("SLA_Analysis","Snapshot SLA by cohort","SLA compliance – all tickets","SLA_Type","Compliance_Rate","bar","K3","R18",3);
chart("Backlog_Analysis","Age Bucket","Snapshot backlog theo tuổi","Segment","Backlog_Count","bar","H3","O18");
chart("Team_Performance","Ownership and actual team effort","Team handling / productive capacity","Team","Utilization","bar","V3","AC18");
for(const [name,range] of [["SLA_Analysis","I5:I55"],["Staffing_Analysis","I5:I1099"]])
 wb.worksheets.getItem(name).getRange(range).conditionalFormats.add("colorScale",{colors:["#EEF4F7","#E8B77B","#C54D4D"]});
console.log((await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:30},maxChars:3000})).ndjson);
console.log((await wb.inspect({kind:"table",range:"README!A4:C13",include:"values,formulas",tableMaxRows:12,tableMaxCols:3,maxChars:2500})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(outputPath);
if(previewDir){
 await fs.mkdir(previewDir,{recursive:true});
 for(const [sheet,range,file] of [["README","A1:L19","workbook_overview.png"],["Demand_Analysis","A1:P18","workbook_demand.png"]]){
  const b=await wb.render({sheetName:sheet,range,scale:1,format:"png"});
  await fs.writeFile(previewDir+"/"+file,new Uint8Array(await b.arrayBuffer()));
 }
}
console.log("Workbook exported: 14 sheets, 5 native charts; static analytical results.");
