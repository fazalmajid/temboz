
(function(){var _jQuery=window.jQuery,_$=window.$;var jQuery=window.jQuery=window.$=function(selector,context){return new jQuery.fn.init(selector,context);};var quickExpr=/^[^<]*(<(.|\s)+>)[^>]*$|^#(\w+)$/,isSimple=/^.[^:#\[\.]*$/,undefined;jQuery.fn=jQuery.prototype={init:function(selector,context){selector=selector||document;if(selector.nodeType){this[0]=selector;this.length=1;return this;}
if(typeof selector=="string"){var match=quickExpr.exec(selector);if(match&&(match[1]||!context)){if(match[1])
selector=jQuery.clean([match[1]],context);else{var elem=document.getElementById(match[3]);if(elem){if(elem.id!=match[3])
return jQuery().find(selector);return jQuery(elem);}
selector=[];}}else
return jQuery(context).find(selector);}else if(jQuery.isFunction(selector))
return jQuery(document)[jQuery.fn.ready?"ready":"load"](selector);return this.setArray(jQuery.makeArray(selector));},jquery:"1.2.6",size:function(){return this.length;},length:0,get:function(num){return num==undefined?jQuery.makeArray(this):this[num];},pushStack:function(elems){var ret=jQuery(elems);ret.prevObject=this;return ret;},setArray:function(elems){this.length=0;Array.prototype.push.apply(this,elems);return this;},each:function(callback,args){return jQuery.each(this,callback,args);},index:function(elem){var ret=-1;return jQuery.inArray(elem&&elem.jquery?elem[0]:elem,this);},attr:function(name,value,type){var options=name;if(name.constructor==String)
if(value===undefined)
return this[0]&&jQuery[type||"attr"](this[0],name);else{options={};options[name]=value;}
return this.each(function(i){for(name in options)
jQuery.attr(type?this.style:this,name,jQuery.prop(this,options[name],type,i,name));});},css:function(key,value){if((key=='width'||key=='height')&&parseFloat(value)<0)
value=undefined;return this.attr(key,value,"curCSS");},text:function(text){if(typeof text!="object"&&text!=null)
return this.empty().append((this[0]&&this[0].ownerDocument||document).createTextNode(text));var ret="";jQuery.each(text||this,function(){jQuery.each(this.childNodes,function(){if(this.nodeType!=8)
ret+=this.nodeType!=1?this.nodeValue:jQuery.fn.text([this]);});});return ret;},wrapAll:function(html){if(this[0])
jQuery(html,this[0].ownerDocument).clone().insertBefore(this[0]).map(function(){var elem=this;while(elem.firstChild)
elem=elem.firstChild;return elem;}).append(this);return this;},wrapInner:function(html){return this.each(function(){jQuery(this).contents().wrapAll(html);});},wrap:function(html){return this.each(function(){jQuery(this).wrapAll(html);});},append:function(){return this.domManip(arguments,true,false,function(elem){if(this.nodeType==1)
this.appendChild(elem);});},prepend:function(){return this.domManip(arguments,true,true,function(elem){if(this.nodeType==1)
this.insertBefore(elem,this.firstChild);});},before:function(){return this.domManip(arguments,false,false,function(elem){this.parentNode.insertBefore(elem,this);});},after:function(){return this.domManip(arguments,false,true,function(elem){this.parentNode.insertBefore(elem,this.nextSibling);});},end:function(){return this.prevObject||jQuery([]);},find:function(selector){var elems=jQuery.map(this,function(elem){return jQuery.find(selector,elem);});return this.pushStack(/[^+>] [^+>]/.test(selector)||selector.indexOf("..")>-1?jQuery.unique(elems):elems);},clone:function(events){var ret=this.map(function(){if(jQuery.browser.msie&&!jQuery.isXMLDoc(this)){var clone=this.cloneNode(true),container=document.createElement("div");container.appendChild(clone);return jQuery.clean([container.innerHTML])[0];}else
return this.cloneNode(true);});var clone=ret.find("*").andSelf().each(function(){if(this[expando]!=undefined)
this[expando]=null;});if(events===true)
this.find("*").andSelf().each(function(i){if(this.nodeType==3)
return;var events=jQuery.data(this,"events");for(var type in events)
for(var handler in events[type])
jQuery.event.add(clone[i],type,events[type][handler],events[type][handler].data);});return ret;},filter:function(selector){return this.pushStack(jQuery.isFunction(selector)&&jQuery.grep(this,function(elem,i){return selector.call(elem,i);})||jQuery.multiFilter(selector,this));},not:function(selector){if(selector.constructor==String)
if(isSimple.test(selector))
return this.pushStack(jQuery.multiFilter(selector,this,true));else
selector=jQuery.multiFilter(selector,this);var isArrayLike=selector.length&&selector[selector.length-1]!==undefined&&!selector.nodeType;return this.filter(function(){return isArrayLike?jQuery.inArray(this,selector)<0:this!=selector;});},add:function(selector){return this.pushStack(jQuery.unique(jQuery.merge(this.get(),typeof selector=='string'?jQuery(selector):jQuery.makeArray(selector))));},is:function(selector){return!!selector&&jQuery.multiFilter(selector,this).length>0;},hasClass:function(selector){return this.is("."+selector);},val:function(value){if(value==undefined){if(this.length){var elem=this[0];if(jQuery.nodeName(elem,"select")){var index=elem.selectedIndex,values=[],options=elem.options,one=elem.type=="select-one";if(index<0)
return null;for(var i=one?index:0,max=one?index+1:options.length;i<max;i++){var option=options[i];if(option.selected){value=jQuery.browser.msie&&!option.attributes.value.specified?option.text:option.value;if(one)
return value;values.push(value);}}
return values;}else
return(this[0].value||"").replace(/\r/g,"");}
return undefined;}
if(value.constructor==Number)
value+='';return this.each(function(){if(this.nodeType!=1)
return;if(value.constructor==Array&&/radio|checkbox/.test(this.type))
this.checked=(jQuery.inArray(this.value,value)>=0||jQuery.inArray(this.name,value)>=0);else if(jQuery.nodeName(this,"select")){var values=jQuery.makeArray(value);jQuery("option",this).each(function(){this.selected=(jQuery.inArray(this.value,values)>=0||jQuery.inArray(this.text,values)>=0);});if(!values.length)
this.selectedIndex=-1;}else
this.value=value;});},html:function(value){return value==undefined?(this[0]?this[0].innerHTML:null):this.empty().append(value);},replaceWith:function(value){return this.after(value).remove();},eq:function(i){return this.slice(i,i+1);},slice:function(){return this.pushStack(Array.prototype.slice.apply(this,arguments));},map:function(callback){return this.pushStack(jQuery.map(this,function(elem,i){return callback.call(elem,i,elem);}));},andSelf:function(){return this.add(this.prevObject);},data:function(key,value){var parts=key.split(".");parts[1]=parts[1]?"."+parts[1]:"";if(value===undefined){var data=this.triggerHandler("getData"+parts[1]+"!",[parts[0]]);if(data===undefined&&this.length)
data=jQuery.data(this[0],key);return data===undefined&&parts[1]?this.data(parts[0]):data;}else
return this.trigger("setData"+parts[1]+"!",[parts[0],value]).each(function(){jQuery.data(this,key,value);});},removeData:function(key){return this.each(function(){jQuery.removeData(this,key);});},domManip:function(args,table,reverse,callback){var clone=this.length>1,elems;return this.each(function(){if(!elems){elems=jQuery.clean(args,this.ownerDocument);if(reverse)
elems.reverse();}
var obj=this;if(table&&jQuery.nodeName(this,"table")&&jQuery.nodeName(elems[0],"tr"))
obj=this.getElementsByTagName("tbody")[0]||this.appendChild(this.ownerDocument.createElement("tbody"));var scripts=jQuery([]);jQuery.each(elems,function(){var elem=clone?jQuery(this).clone(true)[0]:this;if(jQuery.nodeName(elem,"script"))
scripts=scripts.add(elem);else{if(elem.nodeType==1)
scripts=scripts.add(jQuery("script",elem).remove());callback.call(obj,elem);}});scripts.each(evalScript);});}};jQuery.fn.init.prototype=jQuery.fn;function evalScript(i,elem){if(elem.src)
jQuery.ajax({url:elem.src,async:false,dataType:"script"});else
jQuery.globalEval(elem.text||elem.textContent||elem.innerHTML||"");if(elem.parentNode)
elem.parentNode.removeChild(elem);}
function now(){return+new Date;}
jQuery.extend=jQuery.fn.extend=function(){var target=arguments[0]||{},i=1,length=arguments.length,deep=false,options;if(target.constructor==Boolean){deep=target;target=arguments[1]||{};i=2;}
if(typeof target!="object"&&typeof target!="function")
target={};if(length==i){target=this;--i;}
for(;i<length;i++)
if((options=arguments[i])!=null)
for(var name in options){var src=target[name],copy=options[name];if(target===copy)
continue;if(deep&&copy&&typeof copy=="object"&&!copy.nodeType)
target[name]=jQuery.extend(deep,src||(copy.length!=null?[]:{}),copy);else if(copy!==undefined)
target[name]=copy;}
return target;};var expando="jQuery"+now(),uuid=0,windowData={},exclude=/z-?index|font-?weight|opacity|zoom|line-?height/i,defaultView=document.defaultView||{};jQuery.extend({noConflict:function(deep){window.$=_$;if(deep)
window.jQuery=_jQuery;return jQuery;},isFunction:function(fn){return!!fn&&typeof fn!="string"&&!fn.nodeName&&fn.constructor!=Array&&/^[\s[]?function/.test(fn+"");},isXMLDoc:function(elem){return elem.documentElement&&!elem.body||elem.tagName&&elem.ownerDocument&&!elem.ownerDocument.body;},globalEval:function(data){data=jQuery.trim(data);if(data){var head=document.getElementsByTagName("head")[0]||document.documentElement,script=document.createElement("script");script.type="text/javascript";if(jQuery.browser.msie)
script.text=data;else
script.appendChild(document.createTextNode(data));head.insertBefore(script,head.firstChild);head.removeChild(script);}},nodeName:function(elem,name){return elem.nodeName&&elem.nodeName.toUpperCase()==name.toUpperCase();},cache:{},data:function(elem,name,data){elem=elem==window?windowData:elem;var id=elem[expando];if(!id)
id=elem[expando]=++uuid;if(name&&!jQuery.cache[id])
jQuery.cache[id]={};if(data!==undefined)
jQuery.cache[id][name]=data;return name?jQuery.cache[id][name]:id;},removeData:function(elem,name){elem=elem==window?windowData:elem;var id=elem[expando];if(name){if(jQuery.cache[id]){delete jQuery.cache[id][name];name="";for(name in jQuery.cache[id])
break;if(!name)
jQuery.removeData(elem);}}else{try{delete elem[expando];}catch(e){if(elem.removeAttribute)
elem.removeAttribute(expando);}
delete jQuery.cache[id];}},each:function(object,callback,args){var name,i=0,length=object.length;if(args){if(length==undefined){for(name in object)
if(callback.apply(object[name],args)===false)
break;}else
for(;i<length;)
if(callback.apply(object[i++],args)===false)
break;}else{if(length==undefined){for(name in object)
if(callback.call(object[name],name,object[name])===false)
break;}else
for(var value=object[0];i<length&&callback.call(value,i,value)!==false;value=object[++i]){}}
return object;},prop:function(elem,value,type,i,name){if(jQuery.isFunction(value))
value=value.call(elem,i);return value&&value.constructor==Number&&type=="curCSS"&&!exclude.test(name)?value+"px":value;},className:{add:function(elem,classNames){jQuery.each((classNames||"").split(/\s+/),function(i,className){if(elem.nodeType==1&&!jQuery.className.has(elem.className,className))
elem.className+=(elem.className?" ":"")+className;});},remove:function(elem,classNames){if(elem.nodeType==1)
elem.className=classNames!=undefined?jQuery.grep(elem.className.split(/\s+/),function(className){return!jQuery.className.has(classNames,className);}).join(" "):"";},has:function(elem,className){return jQuery.inArray(className,(elem.className||elem).toString().split(/\s+/))>-1;}},swap:function(elem,options,callback){var old={};for(var name in options){old[name]=elem.style[name];elem.style[name]=options[name];}
callback.call(elem);for(var name in options)
elem.style[name]=old[name];},css:function(elem,name,force){if(name=="width"||name=="height"){var val,props={position:"absolute",visibility:"hidden",display:"block"},which=name=="width"?["Left","Right"]:["Top","Bottom"];function getWH(){val=name=="width"?elem.offsetWidth:elem.offsetHeight;var padding=0,border=0;jQuery.each(which,function(){padding+=parseFloat(jQuery.curCSS(elem,"padding"+this,true))||0;border+=parseFloat(jQuery.curCSS(elem,"border"+this+"Width",true))||0;});val-=Math.round(padding+border);}
if(jQuery(elem).is(":visible"))
getWH();else
jQuery.swap(elem,props,getWH);return Math.max(0,val);}
return jQuery.curCSS(elem,name,force);},curCSS:function(elem,name,force){var ret,style=elem.style;function color(elem){if(!jQuery.browser.safari)
return false;var ret=defaultView.getComputedStyle(elem,null);return!ret||ret.getPropertyValue("color")=="";}
if(name=="opacity"&&jQuery.browser.msie){ret=jQuery.attr(style,"opacity");return ret==""?"1":ret;}
if(jQuery.browser.opera&&name=="display"){var save=style.outline;style.outline="0 solid black";style.outline=save;}
if(name.match(/float/i))
name=styleFloat;if(!force&&style&&style[name])
ret=style[name];else if(defaultView.getComputedStyle){if(name.match(/float/i))
name="float";name=name.replace(/([A-Z])/g,"-$1").toLowerCase();var computedStyle=defaultView.getComputedStyle(elem,null);if(computedStyle&&!color(elem))
ret=computedStyle.getPropertyValue(name);else{var swap=[],stack=[],a=elem,i=0;for(;a&&color(a);a=a.parentNode)
stack.unshift(a);for(;i<stack.length;i++)
if(color(stack[i])){swap[i]=stack[i].style.display;stack[i].style.display="block";}
ret=name=="display"&&swap[stack.length-1]!=null?"none":(computedStyle&&computedStyle.getPropertyValue(name))||"";for(i=0;i<swap.length;i++)
if(swap[i]!=null)
stack[i].style.display=swap[i];}
if(name=="opacity"&&ret=="")
ret="1";}else if(elem.currentStyle){var camelCase=name.replace(/\-(\w)/g,function(all,letter){return letter.toUpperCase();});ret=elem.currentStyle[name]||elem.currentStyle[camelCase];if(!/^\d+(px)?$/i.test(ret)&&/^\d/.test(ret)){var left=style.left,rsLeft=elem.runtimeStyle.left;elem.runtimeStyle.left=elem.currentStyle.left;style.left=ret||0;ret=style.pixelLeft+"px";style.left=left;elem.runtimeStyle.left=rsLeft;}}
return ret;},clean:function(elems,context){var ret=[];context=context||document;if(typeof context.createElement=='undefined')
context=context.ownerDocument||context[0]&&context[0].ownerDocument||document;jQuery.each(elems,function(i,elem){if(!elem)
return;if(elem.constructor==Number)
elem+='';if(typeof elem=="string"){elem=elem.replace(/(<(\w+)[^>]*?)\/>/g,function(all,front,tag){return tag.match(/^(abbr|br|col|img|input|link|meta|param|hr|area|embed)$/i)?all:front+"></"+tag+">";});var tags=jQuery.trim(elem).toLowerCase(),div=context.createElement("div");var wrap=!tags.indexOf("<opt")&&[1,"<select multiple='multiple'>","</select>"]||!tags.indexOf("<leg")&&[1,"<fieldset>","</fieldset>"]||tags.match(/^<(thead|tbody|tfoot|colg|cap)/)&&[1,"<table>","</table>"]||!tags.indexOf("<tr")&&[2,"<table><tbody>","</tbody></table>"]||(!tags.indexOf("<td")||!tags.indexOf("<th"))&&[3,"<table><tbody><tr>","</tr></tbody></table>"]||!tags.indexOf("<col")&&[2,"<table><tbody></tbody><colgroup>","</colgroup></table>"]||jQuery.browser.msie&&[1,"div<div>","</div>"]||[0,"",""];div.innerHTML=wrap[1]+elem+wrap[2];while(wrap[0]--)
div=div.lastChild;if(jQuery.browser.msie){var tbody=!tags.indexOf("<table")&&tags.indexOf("<tbody")<0?div.firstChild&&div.firstChild.childNodes:wrap[1]=="<table>"&&tags.indexOf("<tbody")<0?div.childNodes:[];for(var j=tbody.length-1;j>=0;--j)
if(jQuery.nodeName(tbody[j],"tbody")&&!tbody[j].childNodes.length)
tbody[j].parentNode.removeChild(tbody[j]);if(/^\s/.test(elem))
div.insertBefore(context.createTextNode(elem.match(/^\s*/)[0]),div.firstChild);}
elem=jQuery.makeArray(div.childNodes);}
if(elem.length===0&&(!jQuery.nodeName(elem,"form")&&!jQuery.nodeName(elem,"select")))
return;if(elem[0]==undefined||jQuery.nodeName(elem,"form")||elem.options)
ret.push(elem);else
ret=jQuery.merge(ret,elem);});return ret;},attr:function(elem,name,value){if(!elem||elem.nodeType==3||elem.nodeType==8)
return undefined;var notxml=!jQuery.isXMLDoc(elem),set=value!==undefined,msie=jQuery.browser.msie;name=notxml&&jQuery.props[name]||name;if(elem.tagName){var special=/href|src|style/.test(name);if(name=="selected"&&jQuery.browser.safari)
elem.parentNode.selectedIndex;if(name in elem&&notxml&&!special){if(set){if(name=="type"&&jQuery.nodeName(elem,"input")&&elem.parentNode)
throw"type property can't be changed";elem[name]=value;}
if(jQuery.nodeName(elem,"form")&&elem.getAttributeNode(name))
return elem.getAttributeNode(name).nodeValue;return elem[name];}
if(msie&&notxml&&name=="style")
return jQuery.attr(elem.style,"cssText",value);if(set)
elem.setAttribute(name,""+value);var attr=msie&&notxml&&special?elem.getAttribute(name,2):elem.getAttribute(name);return attr===null?undefined:attr;}
if(msie&&name=="opacity"){if(set){elem.zoom=1;elem.filter=(elem.filter||"").replace(/alpha\([^)]*\)/,"")+
(parseInt(value)+''=="NaN"?"":"alpha(opacity="+value*100+")");}
return elem.filter&&elem.filter.indexOf("opacity=")>=0?(parseFloat(elem.filter.match(/opacity=([^)]*)/)[1])/100)+'':"";}
name=name.replace(/-([a-z])/ig,function(all,letter){return letter.toUpperCase();});if(set)
elem[name]=value;return elem[name];},trim:function(text){return(text||"").replace(/^\s+|\s+$/g,"");},makeArray:function(array){var ret=[];if(array!=null){var i=array.length;if(i==null||array.split||array.setInterval||array.call)
ret[0]=array;else
while(i)
ret[--i]=array[i];}
return ret;},inArray:function(elem,array){for(var i=0,length=array.length;i<length;i++)
if(array[i]===elem)
return i;return-1;},merge:function(first,second){var i=0,elem,pos=first.length;if(jQuery.browser.msie){while(elem=second[i++])
if(elem.nodeType!=8)
first[pos++]=elem;}else
while(elem=second[i++])
first[pos++]=elem;return first;},unique:function(array){var ret=[],done={};try{for(var i=0,length=array.length;i<length;i++){var id=jQuery.data(array[i]);if(!done[id]){done[id]=true;ret.push(array[i]);}}}catch(e){ret=array;}
return ret;},grep:function(elems,callback,inv){var ret=[];for(var i=0,length=elems.length;i<length;i++)
if(!inv!=!callback(elems[i],i))
ret.push(elems[i]);return ret;},map:function(elems,callback){var ret=[];for(var i=0,length=elems.length;i<length;i++){var value=callback(elems[i],i);if(value!=null)
ret[ret.length]=value;}
return ret.concat.apply([],ret);}});var userAgent=navigator.userAgent.toLowerCase();jQuery.browser={version:(userAgent.match(/.+(?:rv|it|ra|ie)[\/: ]([\d.]+)/)||[])[1],safari:/webkit/.test(userAgent),opera:/opera/.test(userAgent),msie:/msie/.test(userAgent)&&!/opera/.test(userAgent),mozilla:/mozilla/.test(userAgent)&&!/(compatible|webkit)/.test(userAgent)};var styleFloat=jQuery.browser.msie?"styleFloat":"cssFloat";jQuery.extend({boxModel:!jQuery.browser.msie||document.compatMode=="CSS1Compat",props:{"for":"htmlFor","class":"className","float":styleFloat,cssFloat:styleFloat,styleFloat:styleFloat,readonly:"readOnly",maxlength:"maxLength",cellspacing:"cellSpacing"}});jQuery.each({parent:function(elem){return elem.parentNode;},parents:function(elem){return jQuery.dir(elem,"parentNode");},next:function(elem){return jQuery.nth(elem,2,"nextSibling");},prev:function(elem){return jQuery.nth(elem,2,"previousSibling");},nextAll:function(elem){return jQuery.dir(elem,"nextSibling");},prevAll:function(elem){return jQuery.dir(elem,"previousSibling");},siblings:function(elem){return jQuery.sibling(elem.parentNode.firstChild,elem);},children:function(elem){return jQuery.sibling(elem.firstChild);},contents:function(elem){return jQuery.nodeName(elem,"iframe")?elem.contentDocument||elem.contentWindow.document:jQuery.makeArray(elem.childNodes);}},function(name,fn){jQuery.fn[name]=function(selector){var ret=jQuery.map(this,fn);if(selector&&typeof selector=="string")
ret=jQuery.multiFilter(selector,ret);return this.pushStack(jQuery.unique(ret));};});jQuery.each({appendTo:"append",prependTo:"prepend",insertBefore:"before",insertAfter:"after",replaceAll:"replaceWith"},function(name,original){jQuery.fn[name]=function(){var args=arguments;return this.each(function(){for(var i=0,length=args.length;i<length;i++)
jQuery(args[i])[original](this);});};});jQuery.each({removeAttr:function(name){jQuery.attr(this,name,"");if(this.nodeType==1)
this.removeAttribute(name);},addClass:function(classNames){jQuery.className.add(this,classNames);},removeClass:function(classNames){jQuery.className.remove(this,classNames);},toggleClass:function(classNames){jQuery.className[jQuery.className.has(this,classNames)?"remove":"add"](this,classNames);},remove:function(selector){if(!selector||jQuery.filter(selector,[this]).r.length){jQuery("*",this).add(this).each(function(){jQuery.event.remove(this);jQuery.removeData(this);});if(this.parentNode)
this.parentNode.removeChild(this);}},empty:function(){jQuery(">*",this).remove();while(this.firstChild)
this.removeChild(this.firstChild);}},function(name,fn){jQuery.fn[name]=function(){return this.each(fn,arguments);};});jQuery.each(["Height","Width"],function(i,name){var type=name.toLowerCase();jQuery.fn[type]=function(size){return this[0]==window?jQuery.browser.opera&&document.body["client"+name]||jQuery.browser.safari&&window["inner"+name]||document.compatMode=="CSS1Compat"&&document.documentElement["client"+name]||document.body["client"+name]:this[0]==document?Math.max(Math.max(document.body["scroll"+name],document.documentElement["scroll"+name]),Math.max(document.body["offset"+name],document.documentElement["offset"+name])):size==undefined?(this.length?jQuery.css(this[0],type):null):this.css(type,size.constructor==String?size:size+"px");};});function num(elem,prop){return elem[0]&&parseInt(jQuery.curCSS(elem[0],prop,true),10)||0;}var chars=jQuery.browser.safari&&parseInt(jQuery.browser.version)<417?"(?:[\\w*_-]|\\\\.)":"(?:[\\w\u0128-\uFFFF*_-]|\\\\.)",quickChild=new RegExp("^>\\s*("+chars+"+)"),quickID=new RegExp("^("+chars+"+)(#)("+chars+"+)"),quickClass=new RegExp("^([#.]?)("+chars+"*)");jQuery.extend({expr:{"":function(a,i,m){return m[2]=="*"||jQuery.nodeName(a,m[2]);},"#":function(a,i,m){return a.getAttribute("id")==m[2];},":":{lt:function(a,i,m){return i<m[3]-0;},gt:function(a,i,m){return i>m[3]-0;},nth:function(a,i,m){return m[3]-0==i;},eq:function(a,i,m){return m[3]-0==i;},first:function(a,i){return i==0;},last:function(a,i,m,r){return i==r.length-1;},even:function(a,i){return i%2==0;},odd:function(a,i){return i%2;},"first-child":function(a){return a.parentNode.getElementsByTagName("*")[0]==a;},"last-child":function(a){return jQuery.nth(a.parentNode.lastChild,1,"previousSibling")==a;},"only-child":function(a){return!jQuery.nth(a.parentNode.lastChild,2,"previousSibling");},parent:function(a){return a.firstChild;},empty:function(a){return!a.firstChild;},contains:function(a,i,m){return(a.textContent||a.innerText||jQuery(a).text()||"").indexOf(m[3])>=0;},visible:function(a){return"hidden"!=a.type&&jQuery.css(a,"display")!="none"&&jQuery.css(a,"visibility")!="hidden";},hidden:function(a){return"hidden"==a.type||jQuery.css(a,"display")=="none"||jQuery.css(a,"visibility")=="hidden";},enabled:function(a){return!a.disabled;},disabled:function(a){return a.disabled;},checked:function(a){return a.checked;},selected:function(a){return a.selected||jQuery.attr(a,"selected");},text:function(a){return"text"==a.type;},radio:function(a){return"radio"==a.type;},checkbox:function(a){return"checkbox"==a.type;},file:function(a){return"file"==a.type;},password:function(a){return"password"==a.type;},submit:function(a){return"submit"==a.type;},image:function(a){return"image"==a.type;},reset:function(a){return"reset"==a.type;},button:function(a){return"button"==a.type||jQuery.nodeName(a,"button");},input:function(a){return/input|select|textarea|button/i.test(a.nodeName);},has:function(a,i,m){return jQuery.find(m[3],a).length;},header:function(a){return/h\d/i.test(a.nodeName);},animated:function(a){return jQuery.grep(jQuery.timers,function(fn){return a==fn.elem;}).length;}}},parse:[/^(\[) *@?([\w-]+) *([!*$^~=]*) *('?"?)(.*?)\4 *\]/,/^(:)([\w-]+)\("?'?(.*?(\(.*?\))?[^(]*?)"?'?\)/,new RegExp("^([:.#]*)("+chars+"+)")],multiFilter:function(expr,elems,not){var old,cur=[];while(expr&&expr!=old){old=expr;var f=jQuery.filter(expr,elems,not);expr=f.t.replace(/^\s*,\s*/,"");cur=not?elems=f.r:jQuery.merge(cur,f.r);}
return cur;},find:function(t,context){if(typeof t!="string")
return[t];if(context&&context.nodeType!=1&&context.nodeType!=9)
return[];context=context||document;var ret=[context],done=[],last,nodeName;while(t&&last!=t){var r=[];last=t;t=jQuery.trim(t);var foundToken=false,re=quickChild,m=re.exec(t);if(m){nodeName=m[1].toUpperCase();for(var i=0;ret[i];i++)
for(var c=ret[i].firstChild;c;c=c.nextSibling)
if(c.nodeType==1&&(nodeName=="*"||c.nodeName.toUpperCase()==nodeName))
r.push(c);ret=r;t=t.replace(re,"");if(t.indexOf(" ")==0)continue;foundToken=true;}else{re=/^([>+~])\s*(\w*)/i;if((m=re.exec(t))!=null){r=[];var merge={};nodeName=m[2].toUpperCase();m=m[1];for(var j=0,rl=ret.length;j<rl;j++){var n=m=="~"||m=="+"?ret[j].nextSibling:ret[j].firstChild;for(;n;n=n.nextSibling)
if(n.nodeType==1){var id=jQuery.data(n);if(m=="~"&&merge[id])break;if(!nodeName||n.nodeName.toUpperCase()==nodeName){if(m=="~")merge[id]=true;r.push(n);}
if(m=="+")break;}}
ret=r;t=jQuery.trim(t.replace(re,""));foundToken=true;}}
if(t&&!foundToken){if(!t.indexOf(",")){if(context==ret[0])ret.shift();done=jQuery.merge(done,ret);r=ret=[context];t=" "+t.substr(1,t.length);}else{var re2=quickID;var m=re2.exec(t);if(m){m=[0,m[2],m[3],m[1]];}else{re2=quickClass;m=re2.exec(t);}
m[2]=m[2].replace(/\\/g,"");var elem=ret[ret.length-1];if(m[1]=="#"&&elem&&elem.getElementById&&!jQuery.isXMLDoc(elem)){var oid=elem.getElementById(m[2]);if((jQuery.browser.msie||jQuery.browser.opera)&&oid&&typeof oid.id=="string"&&oid.id!=m[2])
oid=jQuery('[@id="'+m[2]+'"]',elem)[0];ret=r=oid&&(!m[3]||jQuery.nodeName(oid,m[3]))?[oid]:[];}else{for(var i=0;ret[i];i++){var tag=m[1]=="#"&&m[3]?m[3]:m[1]!=""||m[0]==""?"*":m[2];if(tag=="*"&&ret[i].nodeName.toLowerCase()=="object")
tag="param";r=jQuery.merge(r,ret[i].getElementsByTagName(tag));}
if(m[1]==".")
r=jQuery.classFilter(r,m[2]);if(m[1]=="#"){var tmp=[];for(var i=0;r[i];i++)
if(r[i].getAttribute("id")==m[2]){tmp=[r[i]];break;}
r=tmp;}
ret=r;}
t=t.replace(re2,"");}}
if(t){var val=jQuery.filter(t,r);ret=r=val.r;t=jQuery.trim(val.t);}}
if(t)
ret=[];if(ret&&context==ret[0])
ret.shift();done=jQuery.merge(done,ret);return done;},classFilter:function(r,m,not){m=" "+m+" ";var tmp=[];for(var i=0;r[i];i++){var pass=(" "+r[i].className+" ").indexOf(m)>=0;if(!not&&pass||not&&!pass)
tmp.push(r[i]);}
return tmp;},filter:function(t,r,not){var last;while(t&&t!=last){last=t;var p=jQuery.parse,m;for(var i=0;p[i];i++){m=p[i].exec(t);if(m){t=t.substring(m[0].length);m[2]=m[2].replace(/\\/g,"");break;}}
if(!m)
break;if(m[1]==":"&&m[2]=="not")
r=isSimple.test(m[3])?jQuery.filter(m[3],r,true).r:jQuery(r).not(m[3]);else if(m[1]==".")
r=jQuery.classFilter(r,m[2],not);else if(m[1]=="["){var tmp=[],type=m[3];for(var i=0,rl=r.length;i<rl;i++){var a=r[i],z=a[jQuery.props[m[2]]||m[2]];if(z==null||/href|src|selected/.test(m[2]))
z=jQuery.attr(a,m[2])||'';if((type==""&&!!z||type=="="&&z==m[5]||type=="!="&&z!=m[5]||type=="^="&&z&&!z.indexOf(m[5])||type=="$="&&z.substr(z.length-m[5].length)==m[5]||(type=="*="||type=="~=")&&z.indexOf(m[5])>=0)^not)
tmp.push(a);}
r=tmp;}else if(m[1]==":"&&m[2]=="nth-child"){var merge={},tmp=[],test=/(-?)(\d*)n((?:\+|-)?\d*)/.exec(m[3]=="even"&&"2n"||m[3]=="odd"&&"2n+1"||!/\D/.test(m[3])&&"0n+"+m[3]||m[3]),first=(test[1]+(test[2]||1))-0,last=test[3]-0;for(var i=0,rl=r.length;i<rl;i++){var node=r[i],parentNode=node.parentNode,id=jQuery.data(parentNode);if(!merge[id]){var c=1;for(var n=parentNode.firstChild;n;n=n.nextSibling)
if(n.nodeType==1)
n.nodeIndex=c++;merge[id]=true;}
var add=false;if(first==0){if(node.nodeIndex==last)
add=true;}else if((node.nodeIndex-last)%first==0&&(node.nodeIndex-last)/first>=0)
add=true;if(add^not)
tmp.push(node);}
r=tmp;}else{var fn=jQuery.expr[m[1]];if(typeof fn=="object")
fn=fn[m[2]];if(typeof fn=="string")
fn=eval("false||function(a,i){return "+fn+";}");r=jQuery.grep(r,function(elem,i){return fn(elem,i,m,r);},not);}}
return{r:r,t:t};},dir:function(elem,dir){var matched=[],cur=elem[dir];while(cur&&cur!=document){if(cur.nodeType==1)
matched.push(cur);cur=cur[dir];}
return matched;},nth:function(cur,result,dir,elem){result=result||1;var num=0;for(;cur;cur=cur[dir])
if(cur.nodeType==1&&++num==result)
break;return cur;},sibling:function(n,elem){var r=[];for(;n;n=n.nextSibling){if(n.nodeType==1&&n!=elem)
r.push(n);}
return r;}});jQuery.event={add:function(elem,types,handler,data){if(elem.nodeType==3||elem.nodeType==8)
return;if(jQuery.browser.msie&&elem.setInterval)
elem=window;if(!handler.guid)
handler.guid=this.guid++;if(data!=undefined){var fn=handler;handler=this.proxy(fn,function(){return fn.apply(this,arguments);});handler.data=data;}
var events=jQuery.data(elem,"events")||jQuery.data(elem,"events",{}),handle=jQuery.data(elem,"handle")||jQuery.data(elem,"handle",function(){if(typeof jQuery!="undefined"&&!jQuery.event.triggered)
return jQuery.event.handle.apply(arguments.callee.elem,arguments);});handle.elem=elem;jQuery.each(types.split(/\s+/),function(index,type){var parts=type.split(".");type=parts[0];handler.type=parts[1];var handlers=events[type];if(!handlers){handlers=events[type]={};if(!jQuery.event.special[type]||jQuery.event.special[type].setup.call(elem)===false){if(elem.addEventListener)
elem.addEventListener(type,handle,false);else if(elem.attachEvent)
elem.attachEvent("on"+type,handle);}}
handlers[handler.guid]=handler;jQuery.event.global[type]=true;});elem=null;},guid:1,global:{},remove:function(elem,types,handler){if(elem.nodeType==3||elem.nodeType==8)
return;var events=jQuery.data(elem,"events"),ret,index;if(events){if(types==undefined||(typeof types=="string"&&types.charAt(0)=="."))
for(var type in events)
this.remove(elem,type+(types||""));else{if(types.type){handler=types.handler;types=types.type;}
jQuery.each(types.split(/\s+/),function(index,type){var parts=type.split(".");type=parts[0];if(events[type]){if(handler)
delete events[type][handler.guid];else
for(handler in events[type])
if(!parts[1]||events[type][handler].type==parts[1])
delete events[type][handler];for(ret in events[type])break;if(!ret){if(!jQuery.event.special[type]||jQuery.event.special[type].teardown.call(elem)===false){if(elem.removeEventListener)
elem.removeEventListener(type,jQuery.data(elem,"handle"),false);else if(elem.detachEvent)
elem.detachEvent("on"+type,jQuery.data(elem,"handle"));}
ret=null;delete events[type];}}});}
for(ret in events)break;if(!ret){var handle=jQuery.data(elem,"handle");if(handle)handle.elem=null;jQuery.removeData(elem,"events");jQuery.removeData(elem,"handle");}}},trigger:function(type,data,elem,donative,extra){data=jQuery.makeArray(data);if(type.indexOf("!")>=0){type=type.slice(0,-1);var exclusive=true;}
if(!elem){if(this.global[type])
jQuery("*").add([window,document]).trigger(type,data);}else{if(elem.nodeType==3||elem.nodeType==8)
return undefined;var val,ret,fn=jQuery.isFunction(elem[type]||null),event=!data[0]||!data[0].preventDefault;if(event){data.unshift({type:type,target:elem,preventDefault:function(){},stopPropagation:function(){},timeStamp:now()});data[0][expando]=true;}
data[0].type=type;if(exclusive)
data[0].exclusive=true;var handle=jQuery.data(elem,"handle");if(handle)
val=handle.apply(elem,data);if((!fn||(jQuery.nodeName(elem,'a')&&type=="click"))&&elem["on"+type]&&elem["on"+type].apply(elem,data)===false)
val=false;if(event)
data.shift();if(extra&&jQuery.isFunction(extra)){ret=extra.apply(elem,val==null?data:data.concat(val));if(ret!==undefined)
val=ret;}
if(fn&&donative!==false&&val!==false&&!(jQuery.nodeName(elem,'a')&&type=="click")){this.triggered=true;try{elem[type]();}catch(e){}}
this.triggered=false;}
return val;},handle:function(event){var val,ret,namespace,all,handlers;event=arguments[0]=jQuery.event.fix(event||window.event);namespace=event.type.split(".");event.type=namespace[0];namespace=namespace[1];all=!namespace&&!event.exclusive;handlers=(jQuery.data(this,"events")||{})[event.type];for(var j in handlers){var handler=handlers[j];if(all||handler.type==namespace){event.handler=handler;event.data=handler.data;ret=handler.apply(this,arguments);if(val!==false)
val=ret;if(ret===false){event.preventDefault();event.stopPropagation();}}}
return val;},fix:function(event){if(event[expando]==true)
return event;var originalEvent=event;event={originalEvent:originalEvent};var props="altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode metaKey newValue originalTarget pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target timeStamp toElement type view wheelDelta which".split(" ");for(var i=props.length;i;i--)
event[props[i]]=originalEvent[props[i]];event[expando]=true;event.preventDefault=function(){if(originalEvent.preventDefault)
originalEvent.preventDefault();originalEvent.returnValue=false;};event.stopPropagation=function(){if(originalEvent.stopPropagation)
originalEvent.stopPropagation();originalEvent.cancelBubble=true;};event.timeStamp=event.timeStamp||now();if(!event.target)
event.target=event.srcElement||document;if(event.target.nodeType==3)
event.target=event.target.parentNode;if(!event.relatedTarget&&event.fromElement)
event.relatedTarget=event.fromElement==event.target?event.toElement:event.fromElement;if(event.pageX==null&&event.clientX!=null){var doc=document.documentElement,body=document.body;event.pageX=event.clientX+(doc&&doc.scrollLeft||body&&body.scrollLeft||0)-(doc.clientLeft||0);event.pageY=event.clientY+(doc&&doc.scrollTop||body&&body.scrollTop||0)-(doc.clientTop||0);}
if(!event.which&&((event.charCode||event.charCode===0)?event.charCode:event.keyCode))
event.which=event.charCode||event.keyCode;if(!event.metaKey&&event.ctrlKey)
event.metaKey=event.ctrlKey;if(!event.which&&event.button)
event.which=(event.button&1?1:(event.button&2?3:(event.button&4?2:0)));return event;},proxy:function(fn,proxy){proxy.guid=fn.guid=fn.guid||proxy.guid||this.guid++;return proxy;},special:{ready:{setup:function(){bindReady();return;},teardown:function(){return;}},mouseenter:{setup:function(){if(jQuery.browser.msie)return false;jQuery(this).bind("mouseover",jQuery.event.special.mouseenter.handler);return true;},teardown:function(){if(jQuery.browser.msie)return false;jQuery(this).unbind("mouseover",jQuery.event.special.mouseenter.handler);return true;},handler:function(event){if(withinElement(event,this))return true;event.type="mouseenter";return jQuery.event.handle.apply(this,arguments);}},mouseleave:{setup:function(){if(jQuery.browser.msie)return false;jQuery(this).bind("mouseout",jQuery.event.special.mouseleave.handler);return true;},teardown:function(){if(jQuery.browser.msie)return false;jQuery(this).unbind("mouseout",jQuery.event.special.mouseleave.handler);return true;},handler:function(event){if(withinElement(event,this))return true;event.type="mouseleave";return jQuery.event.handle.apply(this,arguments);}}}};jQuery.fn.extend({bind:function(type,data,fn){return type=="unload"?this.one(type,data,fn):this.each(function(){jQuery.event.add(this,type,fn||data,fn&&data);});},one:function(type,data,fn){var one=jQuery.event.proxy(fn||data,function(event){jQuery(this).unbind(event,one);return(fn||data).apply(this,arguments);});return this.each(function(){jQuery.event.add(this,type,one,fn&&data);});},unbind:function(type,fn){return this.each(function(){jQuery.event.remove(this,type,fn);});},trigger:function(type,data,fn){return this.each(function(){jQuery.event.trigger(type,data,this,true,fn);});},triggerHandler:function(type,data,fn){return this[0]&&jQuery.event.trigger(type,data,this[0],false,fn);},toggle:function(fn){var args=arguments,i=1;while(i<args.length)
jQuery.event.proxy(fn,args[i++]);return this.click(jQuery.event.proxy(fn,function(event){this.lastToggle=(this.lastToggle||0)%i;event.preventDefault();return args[this.lastToggle++].apply(this,arguments)||false;}));},hover:function(fnOver,fnOut){return this.bind('mouseenter',fnOver).bind('mouseleave',fnOut);},ready:function(fn){bindReady();if(jQuery.isReady)
fn.call(document,jQuery);else
jQuery.readyList.push(function(){return fn.call(this,jQuery);});return this;}});jQuery.extend({isReady:false,readyList:[],ready:function(){if(!jQuery.isReady){jQuery.isReady=true;if(jQuery.readyList){jQuery.each(jQuery.readyList,function(){this.call(document);});jQuery.readyList=null;}
jQuery(document).triggerHandler("ready");}}});var readyBound=false;function bindReady(){if(readyBound)return;readyBound=true;if(document.addEventListener&&!jQuery.browser.opera)
document.addEventListener("DOMContentLoaded",jQuery.ready,false);if(jQuery.browser.msie&&window==top)(function(){if(jQuery.isReady)return;try{document.documentElement.doScroll("left");}catch(error){setTimeout(arguments.callee,0);return;}
jQuery.ready();})();if(jQuery.browser.opera)
document.addEventListener("DOMContentLoaded",function(){if(jQuery.isReady)return;for(var i=0;i<document.styleSheets.length;i++)
if(document.styleSheets[i].disabled){setTimeout(arguments.callee,0);return;}
jQuery.ready();},false);if(jQuery.browser.safari){var numStyles;(function(){if(jQuery.isReady)return;if(document.readyState!="loaded"&&document.readyState!="complete"){setTimeout(arguments.callee,0);return;}
if(numStyles===undefined)
numStyles=jQuery("style, link[rel=stylesheet]").length;if(document.styleSheets.length!=numStyles){setTimeout(arguments.callee,0);return;}
jQuery.ready();})();}
jQuery.event.add(window,"load",jQuery.ready);}
jQuery.each(("blur,focus,load,resize,scroll,unload,click,dblclick,"+"mousedown,mouseup,mousemove,mouseover,mouseout,change,select,"+"submit,keydown,keypress,keyup,error").split(","),function(i,name){jQuery.fn[name]=function(fn){return fn?this.bind(name,fn):this.trigger(name);};});var withinElement=function(event,elem){var parent=event.relatedTarget;while(parent&&parent!=elem)try{parent=parent.parentNode;}catch(error){parent=elem;}
return parent==elem;};jQuery(window).bind("unload",function(){jQuery("*").add(document).unbind();});jQuery.fn.extend({_load:jQuery.fn.load,load:function(url,params,callback){if(typeof url!='string')
return this._load(url);var off=url.indexOf(" ");if(off>=0){var selector=url.slice(off,url.length);url=url.slice(0,off);}
callback=callback||function(){};var type="GET";if(params)
if(jQuery.isFunction(params)){callback=params;params=null;}else{params=jQuery.param(params);type="POST";}
var self=this;jQuery.ajax({url:url,type:type,dataType:"html",data:params,complete:function(res,status){if(status=="success"||status=="notmodified")
self.html(selector?jQuery("<div/>").append(res.responseText.replace(/<script(.|\s)*?\/script>/g,"")).find(selector):res.responseText);self.each(callback,[res.responseText,status,res]);}});return this;},serialize:function(){return jQuery.param(this.serializeArray());},serializeArray:function(){return this.map(function(){return jQuery.nodeName(this,"form")?jQuery.makeArray(this.elements):this;}).filter(function(){return this.name&&!this.disabled&&(this.checked||/select|textarea/i.test(this.nodeName)||/text|hidden|password/i.test(this.type));}).map(function(i,elem){var val=jQuery(this).val();return val==null?null:val.constructor==Array?jQuery.map(val,function(val,i){return{name:elem.name,value:val};}):{name:elem.name,value:val};}).get();}});jQuery.each("ajaxStart,ajaxStop,ajaxComplete,ajaxError,ajaxSuccess,ajaxSend".split(","),function(i,o){jQuery.fn[o]=function(f){return this.bind(o,f);};});var jsc=now();jQuery.extend({get:function(url,data,callback,type){if(jQuery.isFunction(data)){callback=data;data=null;}
return jQuery.ajax({type:"GET",url:url,data:data,success:callback,dataType:type});},getScript:function(url,callback){return jQuery.get(url,null,callback,"script");},getJSON:function(url,data,callback){return jQuery.get(url,data,callback,"json");},post:function(url,data,callback,type){if(jQuery.isFunction(data)){callback=data;data={};}
return jQuery.ajax({type:"POST",url:url,data:data,success:callback,dataType:type});},ajaxSetup:function(settings){jQuery.extend(jQuery.ajaxSettings,settings);},ajaxSettings:{url:location.href,global:true,type:"GET",timeout:0,contentType:"application/x-www-form-urlencoded",processData:true,async:true,data:null,username:null,password:null,accepts:{xml:"application/xml, text/xml",html:"text/html",script:"text/javascript, application/javascript",json:"application/json, text/javascript",text:"text/plain",_default:"*/*"}},lastModified:{},ajax:function(s){s=jQuery.extend(true,s,jQuery.extend(true,{},jQuery.ajaxSettings,s));var jsonp,jsre=/=\?(&|$)/g,status,data,type=s.type.toUpperCase();if(s.data&&s.processData&&typeof s.data!="string")
s.data=jQuery.param(s.data);if(s.dataType=="jsonp"){if(type=="GET"){if(!s.url.match(jsre))
s.url+=(s.url.match(/\?/)?"&":"?")+(s.jsonp||"callback")+"=?";}else if(!s.data||!s.data.match(jsre))
s.data=(s.data?s.data+"&":"")+(s.jsonp||"callback")+"=?";s.dataType="json";}
if(s.dataType=="json"&&(s.data&&s.data.match(jsre)||s.url.match(jsre))){jsonp="jsonp"+jsc++;if(s.data)
s.data=(s.data+"").replace(jsre,"="+jsonp+"$1");s.url=s.url.replace(jsre,"="+jsonp+"$1");s.dataType="script";window[jsonp]=function(tmp){data=tmp;success();complete();window[jsonp]=undefined;try{delete window[jsonp];}catch(e){}
if(head)
head.removeChild(script);};}
if(s.dataType=="script"&&s.cache==null)
s.cache=false;if(s.cache===false&&type=="GET"){var ts=now();var ret=s.url.replace(/(\?|&)_=.*?(&|$)/,"$1_="+ts+"$2");s.url=ret+((ret==s.url)?(s.url.match(/\?/)?"&":"?")+"_="+ts:"");}
if(s.data&&type=="GET"){s.url+=(s.url.match(/\?/)?"&":"?")+s.data;s.data=null;}
if(s.global&&!jQuery.active++)
jQuery.event.trigger("ajaxStart");var remote=/^(?:\w+:)?\/\/([^\/?#]+)/;if(s.dataType=="script"&&type=="GET"&&remote.test(s.url)&&remote.exec(s.url)[1]!=location.host){var head=document.getElementsByTagName("head")[0];var script=document.createElement("script");script.src=s.url;if(s.scriptCharset)
script.charset=s.scriptCharset;if(!jsonp){var done=false;script.onload=script.onreadystatechange=function(){if(!done&&(!this.readyState||this.readyState=="loaded"||this.readyState=="complete")){done=true;success();complete();head.removeChild(script);}};}
head.appendChild(script);return undefined;}
var requestDone=false;var xhr=window.ActiveXObject?new ActiveXObject("Microsoft.XMLHTTP"):new XMLHttpRequest();if(s.username)
xhr.open(type,s.url,s.async,s.username,s.password);else
xhr.open(type,s.url,s.async);try{if(s.data)
xhr.setRequestHeader("Content-Type",s.contentType);if(s.ifModified)
xhr.setRequestHeader("If-Modified-Since",jQuery.lastModified[s.url]||"Thu, 01 Jan 1970 00:00:00 GMT");xhr.setRequestHeader("X-Requested-With","XMLHttpRequest");xhr.setRequestHeader("Accept",s.dataType&&s.accepts[s.dataType]?s.accepts[s.dataType]+", */*":s.accepts._default);}catch(e){}
if(s.beforeSend&&s.beforeSend(xhr,s)===false){s.global&&jQuery.active--;xhr.abort();return false;}
if(s.global)
jQuery.event.trigger("ajaxSend",[xhr,s]);var onreadystatechange=function(isTimeout){if(!requestDone&&xhr&&(xhr.readyState==4||isTimeout=="timeout")){requestDone=true;if(ival){clearInterval(ival);ival=null;}
status=isTimeout=="timeout"&&"timeout"||!jQuery.httpSuccess(xhr)&&"error"||s.ifModified&&jQuery.httpNotModified(xhr,s.url)&&"notmodified"||"success";if(status=="success"){try{data=jQuery.httpData(xhr,s.dataType,s.dataFilter);}catch(e){status="parsererror";}}
if(status=="success"){var modRes;try{modRes=xhr.getResponseHeader("Last-Modified");}catch(e){}
if(s.ifModified&&modRes)
jQuery.lastModified[s.url]=modRes;if(!jsonp)
success();}else
jQuery.handleError(s,xhr,status);complete();if(s.async)
xhr=null;}};if(s.async){var ival=setInterval(onreadystatechange,13);if(s.timeout>0)
setTimeout(function(){if(xhr){xhr.abort();if(!requestDone)
onreadystatechange("timeout");}},s.timeout);}
try{xhr.send(s.data);}catch(e){jQuery.handleError(s,xhr,null,e);}
if(!s.async)
onreadystatechange();function success(){if(s.success)
s.success(data,status);if(s.global)
jQuery.event.trigger("ajaxSuccess",[xhr,s]);}
function complete(){if(s.complete)
s.complete(xhr,status);if(s.global)
jQuery.event.trigger("ajaxComplete",[xhr,s]);if(s.global&&!--jQuery.active)
jQuery.event.trigger("ajaxStop");}
return xhr;},handleError:function(s,xhr,status,e){if(s.error)s.error(xhr,status,e);if(s.global)
jQuery.event.trigger("ajaxError",[xhr,s,e]);},active:0,httpSuccess:function(xhr){try{return!xhr.status&&location.protocol=="file:"||(xhr.status>=200&&xhr.status<300)||xhr.status==304||xhr.status==1223||jQuery.browser.safari&&xhr.status==undefined;}catch(e){}
return false;},httpNotModified:function(xhr,url){try{var xhrRes=xhr.getResponseHeader("Last-Modified");return xhr.status==304||xhrRes==jQuery.lastModified[url]||jQuery.browser.safari&&xhr.status==undefined;}catch(e){}
return false;},httpData:function(xhr,type,filter){var ct=xhr.getResponseHeader("content-type"),xml=type=="xml"||!type&&ct&&ct.indexOf("xml")>=0,data=xml?xhr.responseXML:xhr.responseText;if(xml&&data.documentElement.tagName=="parsererror")
throw"parsererror";if(filter)
data=filter(data,type);if(type=="script")
jQuery.globalEval(data);if(type=="json")
data=eval("("+data+")");return data;},param:function(a){var s=[];if(a.constructor==Array||a.jquery)
jQuery.each(a,function(){s.push(encodeURIComponent(this.name)+"="+encodeURIComponent(this.value));});else
for(var j in a)
if(a[j]&&a[j].constructor==Array)
jQuery.each(a[j],function(){s.push(encodeURIComponent(j)+"="+encodeURIComponent(this));});else
s.push(encodeURIComponent(j)+"="+encodeURIComponent(jQuery.isFunction(a[j])?a[j]():a[j]));return s.join("&").replace(/%20/g,"+");}});jQuery.fn.extend({show:function(speed,callback){return speed?this.animate({height:"show",width:"show",opacity:"show"},speed,callback):this.filter(":hidden").each(function(){this.style.display=this.oldblock||"";if(jQuery.css(this,"display")=="none"){var elem=jQuery("<"+this.tagName+" />").appendTo("body");this.style.display=elem.css("display");if(this.style.display=="none")
this.style.display="block";elem.remove();}}).end();},hide:function(speed,callback){return speed?this.animate({height:"hide",width:"hide",opacity:"hide"},speed,callback):this.filter(":visible").each(function(){this.oldblock=this.oldblock||jQuery.css(this,"display");this.style.display="none";}).end();},_toggle:jQuery.fn.toggle,toggle:function(fn,fn2){return jQuery.isFunction(fn)&&jQuery.isFunction(fn2)?this._toggle.apply(this,arguments):fn?this.animate({height:"toggle",width:"toggle",opacity:"toggle"},fn,fn2):this.each(function(){jQuery(this)[jQuery(this).is(":hidden")?"show":"hide"]();});},slideDown:function(speed,callback){return this.animate({height:"show"},speed,callback);},slideUp:function(speed,callback){return this.animate({height:"hide"},speed,callback);},slideToggle:function(speed,callback){return this.animate({height:"toggle"},speed,callback);},fadeIn:function(speed,callback){return this.animate({opacity:"show"},speed,callback);},fadeOut:function(speed,callback){return this.animate({opacity:"hide"},speed,callback);},fadeTo:function(speed,to,callback){return this.animate({opacity:to},speed,callback);},animate:function(prop,speed,easing,callback){var optall=jQuery.speed(speed,easing,callback);return this[optall.queue===false?"each":"queue"](function(){if(this.nodeType!=1)
return false;var opt=jQuery.extend({},optall),p,hidden=jQuery(this).is(":hidden"),self=this;for(p in prop){if(prop[p]=="hide"&&hidden||prop[p]=="show"&&!hidden)
return opt.complete.call(this);if(p=="height"||p=="width"){opt.display=jQuery.css(this,"display");opt.overflow=this.style.overflow;}}
if(opt.overflow!=null)
this.style.overflow="hidden";opt.curAnim=jQuery.extend({},prop);jQuery.each(prop,function(name,val){var e=new jQuery.fx(self,opt,name);if(/toggle|show|hide/.test(val))
e[val=="toggle"?hidden?"show":"hide":val](prop);else{var parts=val.toString().match(/^([+-]=)?([\d+-.]+)(.*)$/),start=e.cur(true)||0;if(parts){var end=parseFloat(parts[2]),unit=parts[3]||"px";if(unit!="px"){self.style[name]=(end||1)+unit;start=((end||1)/e.cur(true))*start;self.style[name]=start+unit;}
if(parts[1])
end=((parts[1]=="-="?-1:1)*end)+start;e.custom(start,end,unit);}else
e.custom(start,val,"");}});return true;});},queue:function(type,fn){if(jQuery.isFunction(type)||(type&&type.constructor==Array)){fn=type;type="fx";}
if(!type||(typeof type=="string"&&!fn))
return queue(this[0],type);return this.each(function(){if(fn.constructor==Array)
queue(this,type,fn);else{queue(this,type).push(fn);if(queue(this,type).length==1)
fn.call(this);}});},stop:function(clearQueue,gotoEnd){var timers=jQuery.timers;if(clearQueue)
this.queue([]);this.each(function(){for(var i=timers.length-1;i>=0;i--)
if(timers[i].elem==this){if(gotoEnd)
timers[i](true);timers.splice(i,1);}});if(!gotoEnd)
this.dequeue();return this;}});var queue=function(elem,type,array){if(elem){type=type||"fx";var q=jQuery.data(elem,type+"queue");if(!q||array)
q=jQuery.data(elem,type+"queue",jQuery.makeArray(array));}
return q;};jQuery.fn.dequeue=function(type){type=type||"fx";return this.each(function(){var q=queue(this,type);q.shift();if(q.length)
q[0].call(this);});};jQuery.extend({speed:function(speed,easing,fn){var opt=speed&&speed.constructor==Object?speed:{complete:fn||!fn&&easing||jQuery.isFunction(speed)&&speed,duration:speed,easing:fn&&easing||easing&&easing.constructor!=Function&&easing};opt.duration=(opt.duration&&opt.duration.constructor==Number?opt.duration:jQuery.fx.speeds[opt.duration])||jQuery.fx.speeds.def;opt.old=opt.complete;opt.complete=function(){if(opt.queue!==false)
jQuery(this).dequeue();if(jQuery.isFunction(opt.old))
opt.old.call(this);};return opt;},easing:{linear:function(p,n,firstNum,diff){return firstNum+diff*p;},swing:function(p,n,firstNum,diff){return((-Math.cos(p*Math.PI)/2)+0.5)*diff+firstNum;}},timers:[],timerId:null,fx:function(elem,options,prop){this.options=options;this.elem=elem;this.prop=prop;if(!options.orig)
options.orig={};}});jQuery.fx.prototype={update:function(){if(this.options.step)
this.options.step.call(this.elem,this.now,this);(jQuery.fx.step[this.prop]||jQuery.fx.step._default)(this);if(this.prop=="height"||this.prop=="width")
this.elem.style.display="block";},cur:function(force){if(this.elem[this.prop]!=null&&this.elem.style[this.prop]==null)
return this.elem[this.prop];var r=parseFloat(jQuery.css(this.elem,this.prop,force));return r&&r>-10000?r:parseFloat(jQuery.curCSS(this.elem,this.prop))||0;},custom:function(from,to,unit){this.startTime=now();this.start=from;this.end=to;this.unit=unit||this.unit||"px";this.now=this.start;this.pos=this.state=0;this.update();var self=this;function t(gotoEnd){return self.step(gotoEnd);}
t.elem=this.elem;jQuery.timers.push(t);if(jQuery.timerId==null){jQuery.timerId=setInterval(function(){var timers=jQuery.timers;for(var i=0;i<timers.length;i++)
if(!timers[i]())
timers.splice(i--,1);if(!timers.length){clearInterval(jQuery.timerId);jQuery.timerId=null;}},13);}},show:function(){this.options.orig[this.prop]=jQuery.attr(this.elem.style,this.prop);this.options.show=true;this.custom(0,this.cur());if(this.prop=="width"||this.prop=="height")
this.elem.style[this.prop]="1px";jQuery(this.elem).show();},hide:function(){this.options.orig[this.prop]=jQuery.attr(this.elem.style,this.prop);this.options.hide=true;this.custom(this.cur(),0);},step:function(gotoEnd){var t=now();if(gotoEnd||t>this.options.duration+this.startTime){this.now=this.end;this.pos=this.state=1;this.update();this.options.curAnim[this.prop]=true;var done=true;for(var i in this.options.curAnim)
if(this.options.curAnim[i]!==true)
done=false;if(done){if(this.options.display!=null){this.elem.style.overflow=this.options.overflow;this.elem.style.display=this.options.display;if(jQuery.css(this.elem,"display")=="none")
this.elem.style.display="block";}
if(this.options.hide)
this.elem.style.display="none";if(this.options.hide||this.options.show)
for(var p in this.options.curAnim)
jQuery.attr(this.elem.style,p,this.options.orig[p]);}
if(done)
this.options.complete.call(this.elem);return false;}else{var n=t-this.startTime;this.state=n/this.options.duration;this.pos=jQuery.easing[this.options.easing||(jQuery.easing.swing?"swing":"linear")](this.state,n,0,1,this.options.duration);this.now=this.start+((this.end-this.start)*this.pos);this.update();}
return true;}};jQuery.extend(jQuery.fx,{speeds:{slow:600,fast:200,def:400},step:{scrollLeft:function(fx){fx.elem.scrollLeft=fx.now;},scrollTop:function(fx){fx.elem.scrollTop=fx.now;},opacity:function(fx){jQuery.attr(fx.elem.style,"opacity",fx.now);},_default:function(fx){fx.elem.style[fx.prop]=fx.now+fx.unit;}}});jQuery.fn.offset=function(){var left=0,top=0,elem=this[0],results;if(elem)with(jQuery.browser){var parent=elem.parentNode,offsetChild=elem,offsetParent=elem.offsetParent,doc=elem.ownerDocument,safari2=safari&&parseInt(version)<522&&!/adobeair/i.test(userAgent),css=jQuery.curCSS,fixed=css(elem,"position")=="fixed";if(elem.getBoundingClientRect){var box=elem.getBoundingClientRect();add(box.left+Math.max(doc.documentElement.scrollLeft,doc.body.scrollLeft),box.top+Math.max(doc.documentElement.scrollTop,doc.body.scrollTop));add(-doc.documentElement.clientLeft,-doc.documentElement.clientTop);}else{add(elem.offsetLeft,elem.offsetTop);while(offsetParent){add(offsetParent.offsetLeft,offsetParent.offsetTop);if(mozilla&&!/^t(able|d|h)$/i.test(offsetParent.tagName)||safari&&!safari2)
border(offsetParent);if(!fixed&&css(offsetParent,"position")=="fixed")
fixed=true;offsetChild=/^body$/i.test(offsetParent.tagName)?offsetChild:offsetParent;offsetParent=offsetParent.offsetParent;}
while(parent&&parent.tagName&&!/^body|html$/i.test(parent.tagName)){if(!/^inline|table.*$/i.test(css(parent,"display")))
add(-parent.scrollLeft,-parent.scrollTop);if(mozilla&&css(parent,"overflow")!="visible")
border(parent);parent=parent.parentNode;}
if((safari2&&(fixed||css(offsetChild,"position")=="absolute"))||(mozilla&&css(offsetChild,"position")!="absolute"))
add(-doc.body.offsetLeft,-doc.body.offsetTop);if(fixed)
add(Math.max(doc.documentElement.scrollLeft,doc.body.scrollLeft),Math.max(doc.documentElement.scrollTop,doc.body.scrollTop));}
results={top:top,left:left};}
function border(elem){add(jQuery.curCSS(elem,"borderLeftWidth",true),jQuery.curCSS(elem,"borderTopWidth",true));}
function add(l,t){left+=parseInt(l,10)||0;top+=parseInt(t,10)||0;}
return results;};jQuery.fn.extend({position:function(){var left=0,top=0,results;if(this[0]){var offsetParent=this.offsetParent(),offset=this.offset(),parentOffset=/^body|html$/i.test(offsetParent[0].tagName)?{top:0,left:0}:offsetParent.offset();offset.top-=num(this,'marginTop');offset.left-=num(this,'marginLeft');parentOffset.top+=num(offsetParent,'borderTopWidth');parentOffset.left+=num(offsetParent,'borderLeftWidth');results={top:offset.top-parentOffset.top,left:offset.left-parentOffset.left};}
return results;},offsetParent:function(){var offsetParent=this[0].offsetParent;while(offsetParent&&(!/^body|html$/i.test(offsetParent.tagName)&&jQuery.css(offsetParent,'position')=='static'))
offsetParent=offsetParent.offsetParent;return jQuery(offsetParent);}});jQuery.each(['Left','Top'],function(i,name){var method='scroll'+name;jQuery.fn[method]=function(val){if(!this[0])return;return val!=undefined?this.each(function(){this==window||this==document?window.scrollTo(!i?val:jQuery(window).scrollLeft(),i?val:jQuery(window).scrollTop()):this[method]=val;}):this[0]==window||this[0]==document?self[i?'pageYOffset':'pageXOffset']||jQuery.boxModel&&document.documentElement[method]||document.body[method]:this[0][method];};});jQuery.each(["Height","Width"],function(i,name){var tl=i?"Left":"Top",br=i?"Right":"Bottom";jQuery.fn["inner"+name]=function(){return this[name.toLowerCase()]()+
num(this,"padding"+tl)+
num(this,"padding"+br);};jQuery.fn["outer"+name]=function(margin){return this["inner"+name]()+
num(this,"border"+tl+"Width")+
num(this,"border"+br+"Width")+
(margin?num(this,"margin"+tl)+num(this,"margin"+br):0);};});})();(function($){$.fn.ajaxSubmit=function(options){if(!this.length){log('ajaxSubmit: skipping submit process - no element selected');return this;}
if(typeof options=='function')
options={success:options};options=$.extend({url:this.attr('action')||window.location.toString(),type:this.attr('method')||'GET'},options||{});var veto={};this.trigger('form-pre-serialize',[this,options,veto]);if(veto.veto){log('ajaxSubmit: submit vetoed via form-pre-serialize trigger');return this;}
var a=this.formToArray(options.semantic);if(options.data){options.extraData=options.data;for(var n in options.data)
a.push({name:n,value:options.data[n]});}
if(options.beforeSubmit&&options.beforeSubmit(a,this,options)===false){log('ajaxSubmit: submit aborted via beforeSubmit callback');return this;}
this.trigger('form-submit-validate',[a,this,options,veto]);if(veto.veto){log('ajaxSubmit: submit vetoed via form-submit-validate trigger');return this;}
var q=$.param(a);if(options.type.toUpperCase()=='GET'){options.url+=(options.url.indexOf('?')>=0?'&':'?')+q;options.data=null;}
else
options.data=q;var $form=this,callbacks=[];if(options.resetForm)callbacks.push(function(){$form.resetForm();});if(options.clearForm)callbacks.push(function(){$form.clearForm();});if(!options.dataType&&options.target){var oldSuccess=options.success||function(){};callbacks.push(function(data){$(options.target).html(data).each(oldSuccess,arguments);});}
else if(options.success)
callbacks.push(options.success);options.success=function(data,status){for(var i=0,max=callbacks.length;i<max;i++)
callbacks[i](data,status,$form);};var files=$('input:file',this).fieldValue();var found=false;for(var j=0;j<files.length;j++)
if(files[j])
found=true;if(options.iframe||found){if($.browser.safari&&options.closeKeepAlive)
$.get(options.closeKeepAlive,fileUpload);else
fileUpload();}
else
$.ajax(options);this.trigger('form-submit-notify',[this,options]);return this;function fileUpload(){var form=$form[0];if($(':input[@name=submit]',form).length){alert('Error: Form elements must not be named "submit".');return;}
var opts=$.extend({},$.ajaxSettings,options);var id='jqFormIO'+(new Date().getTime());var $io=$('<iframe id="'+id+'" name="'+id+'" />');var io=$io[0];if($.browser.msie||$.browser.opera)
io.src='javascript:false;document.write("");';$io.css({position:'absolute',top:'-1000px',left:'-1000px'});var xhr={responseText:null,responseXML:null,status:0,statusText:'n/a',getAllResponseHeaders:function(){},getResponseHeader:function(){},setRequestHeader:function(){}};var g=opts.global;if(g&&!$.active++)$.event.trigger("ajaxStart");if(g)$.event.trigger("ajaxSend",[xhr,opts]);var cbInvoked=0;var timedOut=0;var sub=form.clk;if(sub){var n=sub.name;if(n&&!sub.disabled){options.extraData=options.extraData||{};options.extraData[n]=sub.value;if(sub.type=="image"){options.extraData[name+'.x']=form.clk_x;options.extraData[name+'.y']=form.clk_y;}}}
setTimeout(function(){var t=$form.attr('target'),a=$form.attr('action');$form.attr({target:id,encoding:'multipart/form-data',enctype:'multipart/form-data',method:'POST',action:opts.url});if(opts.timeout)
setTimeout(function(){timedOut=true;cb();},opts.timeout);var extraInputs=[];try{if(options.extraData)
for(var n in options.extraData)
extraInputs.push($('<input type="hidden" name="'+n+'" value="'+options.extraData[n]+'" />').appendTo(form)[0]);$io.appendTo('body');io.attachEvent?io.attachEvent('onload',cb):io.addEventListener('load',cb,false);form.submit();}
finally{$form.attr('action',a);t?$form.attr('target',t):$form.removeAttr('target');$(extraInputs).remove();}},10);function cb(){if(cbInvoked++)return;io.detachEvent?io.detachEvent('onload',cb):io.removeEventListener('load',cb,false);var operaHack=0;var ok=true;try{if(timedOut)throw'timeout';var data,doc;doc=io.contentWindow?io.contentWindow.document:io.contentDocument?io.contentDocument:io.document;if(doc.body==null&&!operaHack&&$.browser.opera){operaHack=1;cbInvoked--;setTimeout(cb,100);return;}
xhr.responseText=doc.body?doc.body.innerHTML:null;xhr.responseXML=doc.XMLDocument?doc.XMLDocument:doc;xhr.getResponseHeader=function(header){var headers={'content-type':opts.dataType};return headers[header];};if(opts.dataType=='json'||opts.dataType=='script'){var ta=doc.getElementsByTagName('textarea')[0];xhr.responseText=ta?ta.value:xhr.responseText;}
else if(opts.dataType=='xml'&&!xhr.responseXML&&xhr.responseText!=null){xhr.responseXML=toXml(xhr.responseText);}
data=$.httpData(xhr,opts.dataType);}
catch(e){ok=false;$.handleError(opts,xhr,'error',e);}
if(ok){opts.success(data,'success');if(g)$.event.trigger("ajaxSuccess",[xhr,opts]);}
if(g)$.event.trigger("ajaxComplete",[xhr,opts]);if(g&&!--$.active)$.event.trigger("ajaxStop");if(opts.complete)opts.complete(xhr,ok?'success':'error');setTimeout(function(){$io.remove();xhr.responseXML=null;},100);};function toXml(s,doc){if(window.ActiveXObject){doc=new ActiveXObject('Microsoft.XMLDOM');doc.async='false';doc.loadXML(s);}
else
doc=(new DOMParser()).parseFromString(s,'text/xml');return(doc&&doc.documentElement&&doc.documentElement.tagName!='parsererror')?doc:null;};};};$.fn.ajaxForm=function(options){return this.ajaxFormUnbind().bind('submit.form-plugin',function(){$(this).ajaxSubmit(options);return false;}).each(function(){$(":submit,input:image",this).bind('click.form-plugin',function(e){var $form=this.form;$form.clk=this;if(this.type=='image'){if(e.offsetX!=undefined){$form.clk_x=e.offsetX;$form.clk_y=e.offsetY;}else if(typeof $.fn.offset=='function'){var offset=$(this).offset();$form.clk_x=e.pageX-offset.left;$form.clk_y=e.pageY-offset.top;}else{$form.clk_x=e.pageX-this.offsetLeft;$form.clk_y=e.pageY-this.offsetTop;}}
setTimeout(function(){$form.clk=$form.clk_x=$form.clk_y=null;},10);});});};$.fn.ajaxFormUnbind=function(){this.unbind('submit.form-plugin');return this.each(function(){$(":submit,input:image",this).unbind('click.form-plugin');});};$.fn.formToArray=function(semantic){var a=[];if(this.length==0)return a;var form=this[0];var els=semantic?form.getElementsByTagName('*'):form.elements;if(!els)return a;for(var i=0,max=els.length;i<max;i++){var el=els[i];var n=el.name;if(!n)continue;if(semantic&&form.clk&&el.type=="image"){if(!el.disabled&&form.clk==el)
a.push({name:n+'.x',value:form.clk_x},{name:n+'.y',value:form.clk_y});continue;}
var v=$.fieldValue(el,true);if(v&&v.constructor==Array){for(var j=0,jmax=v.length;j<jmax;j++)
a.push({name:n,value:v[j]});}
else if(v!==null&&typeof v!='undefined')
a.push({name:n,value:v});}
if(!semantic&&form.clk){var inputs=form.getElementsByTagName("input");for(var i=0,max=inputs.length;i<max;i++){var input=inputs[i];var n=input.name;if(n&&!input.disabled&&input.type=="image"&&form.clk==input)
a.push({name:n+'.x',value:form.clk_x},{name:n+'.y',value:form.clk_y});}}
return a;};$.fn.formSerialize=function(semantic){return $.param(this.formToArray(semantic));};$.fn.fieldSerialize=function(successful){var a=[];this.each(function(){var n=this.name;if(!n)return;var v=$.fieldValue(this,successful);if(v&&v.constructor==Array){for(var i=0,max=v.length;i<max;i++)
a.push({name:n,value:v[i]});}
else if(v!==null&&typeof v!='undefined')
a.push({name:this.name,value:v});});return $.param(a);};$.fn.fieldValue=function(successful){for(var val=[],i=0,max=this.length;i<max;i++){var el=this[i];var v=$.fieldValue(el,successful);if(v===null||typeof v=='undefined'||(v.constructor==Array&&!v.length))
continue;v.constructor==Array?$.merge(val,v):val.push(v);}
return val;};$.fieldValue=function(el,successful){var n=el.name,t=el.type,tag=el.tagName.toLowerCase();if(typeof successful=='undefined')successful=true;if(successful&&(!n||el.disabled||t=='reset'||t=='button'||(t=='checkbox'||t=='radio')&&!el.checked||(t=='submit'||t=='image')&&el.form&&el.form.clk!=el||tag=='select'&&el.selectedIndex==-1))
return null;if(tag=='select'){var index=el.selectedIndex;if(index<0)return null;var a=[],ops=el.options;var one=(t=='select-one');var max=(one?index+1:ops.length);for(var i=(one?index:0);i<max;i++){var op=ops[i];if(op.selected){var v=$.browser.msie&&!(op.attributes['value'].specified)?op.text:op.value;if(one)return v;a.push(v);}}
return a;}
return el.value;};$.fn.clearForm=function(){return this.each(function(){$('input,select,textarea',this).clearFields();});};$.fn.clearFields=$.fn.clearInputs=function(){return this.each(function(){var t=this.type,tag=this.tagName.toLowerCase();if(t=='text'||t=='password'||tag=='textarea')
this.value='';else if(t=='checkbox'||t=='radio')
this.checked=false;else if(tag=='select')
this.selectedIndex=-1;});};$.fn.resetForm=function(){return this.each(function(){if(typeof this.reset=='function'||(typeof this.reset=='object'&&!this.reset.nodeType))
this.reset();});};$.fn.enable=function(b){if(b==undefined)b=true;return this.each(function(){this.disabled=!b});};$.fn.select=function(select){if(select==undefined)select=true;return this.each(function(){var t=this.type;if(t=='checkbox'||t=='radio')
this.checked=select;else if(this.tagName.toLowerCase()=='option'){var $sel=$(this).parent('select');if(select&&$sel[0]&&$sel[0].type=='select-one'){$sel.find('option').select(false);}
this.selected=select;}});};function log(){if($.fn.ajaxSubmit.debug&&window.console&&window.console.log)
window.console.log('[jquery.form] '+Array.prototype.join.call(arguments,''));};})(jQuery);;(function($){$.ui={plugin:{add:function(module,option,set){var proto=$.ui[module].prototype;for(var i in set){proto.plugins[i]=proto.plugins[i]||[];proto.plugins[i].push([option,set[i]]);}},call:function(instance,name,args){var set=instance.plugins[name];if(!set){return;}
for(var i=0;i<set.length;i++){if(instance.options[set[i][0]]){set[i][1].apply(instance.element,args);}}}},cssCache:{},css:function(name){if($.ui.cssCache[name]){return $.ui.cssCache[name];}
var tmp=$('<div class="ui-resizable-gen">').addClass(name).css({position:'absolute',top:'-5000px',left:'-5000px',display:'block'}).appendTo('body');$.ui.cssCache[name]=!!((!(/auto|default/).test(tmp.css('cursor'))||(/^[1-9]/).test(tmp.css('height'))||(/^[1-9]/).test(tmp.css('width'))||!(/none/).test(tmp.css('backgroundImage'))||!(/transparent|rgba\(0, 0, 0, 0\)/).test(tmp.css('backgroundColor'))));try{$('body').get(0).removeChild(tmp.get(0));}catch(e){}
return $.ui.cssCache[name];},disableSelection:function(e){e.unselectable="on";e.onselectstart=function(){return false;};if(e.style){e.style.MozUserSelect="none";}},enableSelection:function(e){e.unselectable="off";e.onselectstart=function(){return true;};if(e.style){e.style.MozUserSelect="";}},hasScroll:function(e,a){var scroll=/top/.test(a||"top")?'scrollTop':'scrollLeft',has=false;if(e[scroll]>0)return true;e[scroll]=1;has=e[scroll]>0?true:false;e[scroll]=0;return has;}};var _remove=$.fn.remove;$.fn.remove=function(){$("*",this).add(this).trigger("remove");return _remove.apply(this,arguments);};function getter(namespace,plugin,method){var methods=$[namespace][plugin].getter||[];methods=(typeof methods=="string"?methods.split(/,?\s+/):methods);return($.inArray(method,methods)!=-1);}
$.widget=function(name,prototype){var namespace=name.split(".")[0];name=name.split(".")[1];$.fn[name]=function(options){var isMethodCall=(typeof options=='string'),args=Array.prototype.slice.call(arguments,1);if(isMethodCall&&getter(namespace,name,options)){var instance=$.data(this[0],name);return(instance?instance[options].apply(instance,args):undefined);}
return this.each(function(){var instance=$.data(this,name);if(isMethodCall&&instance&&$.isFunction(instance[options])){instance[options].apply(instance,args);}else if(!isMethodCall){$.data(this,name,new $[namespace][name](this,options));}});};$[namespace][name]=function(element,options){var self=this;this.widgetName=name;this.widgetBaseClass=namespace+'-'+name;this.options=$.extend({disabled:false},$[namespace][name].defaults,options);this.element=$(element).bind('setData.'+name,function(e,key,value){return self.setData(key,value);}).bind('getData.'+name,function(e,key){return self.getData(key);}).bind('remove',function(){return self.destroy();});this.init();};$[namespace][name].prototype=$.extend({},$.widget.prototype,prototype);};$.widget.prototype={init:function(){},destroy:function(){this.element.removeData(this.widgetName);},getData:function(key){return this.options[key];},setData:function(key,value){this.options[key]=value;if(key=='disabled'){this.element[value?'addClass':'removeClass'](this.widgetBaseClass+'-disabled');}},enable:function(){this.setData('disabled',false);},disable:function(){this.setData('disabled',true);}};$.ui.mouse={mouseInit:function(){var self=this;this.element.bind('mousedown.'+this.widgetName,function(e){return self.mouseDown(e);});if($.browser.msie){this._mouseUnselectable=this.element.attr('unselectable');this.element.attr('unselectable','on');}
this.started=false;},mouseDestroy:function(){this.element.unbind('.'+this.widgetName);($.browser.msie&&this.element.attr('unselectable',this._mouseUnselectable));},mouseDown:function(e){(this._mouseStarted&&this.mouseUp(e));this._mouseDownEvent=e;var self=this,btnIsLeft=(e.which==1),elIsCancel=(typeof this.options.cancel=="string"?$(e.target).is(this.options.cancel):false);if(!btnIsLeft||elIsCancel||!this.mouseCapture(e)){return true;}
this._mouseDelayMet=!this.options.delay;if(!this._mouseDelayMet){this._mouseDelayTimer=setTimeout(function(){self._mouseDelayMet=true;},this.options.delay);}
if(this.mouseDistanceMet(e)&&this.mouseDelayMet(e)){this._mouseStarted=(this.mouseStart(e)!==false);if(!this._mouseStarted){e.preventDefault();return true;}}
this._mouseMoveDelegate=function(e){return self.mouseMove(e);};this._mouseUpDelegate=function(e){return self.mouseUp(e);};$(document).bind('mousemove.'+this.widgetName,this._mouseMoveDelegate).bind('mouseup.'+this.widgetName,this._mouseUpDelegate);return false;},mouseMove:function(e){if($.browser.msie&&!e.button){return this.mouseUp(e);}
if(this._mouseStarted){this.mouseDrag(e);return false;}
if(this.mouseDistanceMet(e)&&this.mouseDelayMet(e)){this._mouseStarted=(this.mouseStart(this._mouseDownEvent,e)!==false);(this._mouseStarted?this.mouseDrag(e):this.mouseUp(e));}
return!this._mouseStarted;},mouseUp:function(e){$(document).unbind('mousemove.'+this.widgetName,this._mouseMoveDelegate).unbind('mouseup.'+this.widgetName,this._mouseUpDelegate);if(this._mouseStarted){this._mouseStarted=false;this.mouseStop(e);}
return false;},mouseDistanceMet:function(e){return(Math.max(Math.abs(this._mouseDownEvent.pageX-e.pageX),Math.abs(this._mouseDownEvent.pageY-e.pageY))>=this.options.distance);},mouseDelayMet:function(e){return this._mouseDelayMet;},mouseStart:function(e){},mouseDrag:function(e){},mouseStop:function(e){},mouseCapture:function(e){return true;}};$.ui.mouse.defaults={cancel:null,distance:1,delay:0};})(jQuery);(function($){var setDataSwitch={dragStart:"start.draggable",drag:"drag.draggable",dragStop:"stop.draggable",maxHeight:"maxHeight.resizable",minHeight:"minHeight.resizable",maxWidth:"maxWidth.resizable",minWidth:"minWidth.resizable",resizeStart:"start.resizable",resize:"drag.resizable",resizeStop:"stop.resizable"};$.widget("ui.dialog",{init:function(){var self=this,options=this.options,resizeHandles=typeof options.resizable=='string'?options.resizable:'n,e,s,w,se,sw,ne,nw',uiDialogContent=this.element.addClass('ui-dialog-content').wrap('<div/>').wrap('<div/>'),uiDialogContainer=uiDialogContent.parent().addClass('ui-dialog-container').css({position:'relative'}),title=options.title||uiDialogContent.attr('title')||'',uiDialogTitlebar=(this.uiDialogTitlebar=$('<div class="ui-dialog-titlebar"/>')).append('<span class="ui-dialog-title">'+title+'</span>').append('<a href="#" class="ui-dialog-titlebar-close"><span>X</span></a>').prependTo(uiDialogContainer),uiDialog=(this.uiDialog=uiDialogContainer.parent()).appendTo(document.body).hide().addClass('ui-dialog').addClass(options.dialogClass).addClass(uiDialogContent.attr('className')).removeClass('ui-dialog-content').css({position:'absolute',width:options.width,height:options.height,overflow:'hidden',zIndex:options.zIndex}).attr('tabIndex',-1).css('outline',0).keydown(function(ev){if(options.closeOnEscape){var ESC=27;(ev.keyCode&&ev.keyCode==ESC&&self.close());}}).mousedown(function(){self.moveToTop();});this.uiDialogTitlebarClose=$('.ui-dialog-titlebar-close',uiDialogTitlebar).hover(function(){$(this).addClass('ui-dialog-titlebar-close-hover');},function(){$(this).removeClass('ui-dialog-titlebar-close-hover');}).mousedown(function(ev){ev.stopPropagation();}).click(function(){self.close();return false;});var hasButtons=false;$.each(options.buttons,function(){return!(hasButtons=true);});if(hasButtons){var uiDialogButtonPane=$('<div class="ui-dialog-buttonpane"/>').appendTo(uiDialog);$.each(options.buttons,function(name,fn){$('<button/>').text(name).click(function(){fn.apply(self.element[0],arguments);}).appendTo(uiDialogButtonPane);});}
if($.fn.draggable){uiDialog.draggable({handle:'.ui-dialog-titlebar',start:function(e,ui){self.moveToTop();(options.dragStart&&options.dragStart.apply(this,arguments));},drag:options.drag,stop:function(e,ui){(options.dragStop&&options.dragStop.apply(this,arguments));$.ui.dialog.overlay.resize();}});(options.draggable||uiDialog.draggable('disable'));}
if($.fn.resizable){uiDialog.resizable({maxWidth:options.maxWidth,maxHeight:options.maxHeight,minWidth:options.minWidth,minHeight:options.minHeight,start:options.resizeStart,resize:options.resize,handles:resizeHandles,stop:function(e,ui){(options.resizeStop&&options.resizeStop.apply(this,arguments));$.ui.dialog.overlay.resize();}});(options.resizable||uiDialog.resizable('disable'));}
(options.bgiframe&&$.fn.bgiframe&&uiDialog.bgiframe());(options.autoOpen&&this.open());},setData:function(key,value){(setDataSwitch[key]&&this.uiDialog.data(setDataSwitch[key],value));switch(key){case"draggable":this.uiDialog.draggable(value?'enable':'disable');break;case"height":this.uiDialog.height(value);break;case"position":this.position(value);break;case"resizable":(typeof value=='string'&&this.uiDialog.data('handles.resizable',value));this.uiDialog.resizable(value?'enable':'disable');break;case"title":$(".ui-dialog-title",this.uiDialogTitlebar).text(value);break;case"width":this.uiDialog.width(value);break;}
$.widget.prototype.setData.apply(this,arguments);},position:function(pos){var wnd=$(window),doc=$(document),pTop=doc.scrollTop(),pLeft=doc.scrollLeft(),minTop=pTop;if($.inArray(pos,['center','top','right','bottom','left'])>=0){pos=[pos=='right'||pos=='left'?pos:'center',pos=='top'||pos=='bottom'?pos:'middle'];}
if(pos.constructor!=Array){pos=['center','middle'];}
if(pos[0].constructor==Number){pLeft+=pos[0];}else{switch(pos[0]){case'left':pLeft+=0;break;case'right':pLeft+=wnd.width()-this.uiDialog.width();break;default:case'center':pLeft+=(wnd.width()-this.uiDialog.width())/2;}}
if(pos[1].constructor==Number){pTop+=pos[1];}else{switch(pos[1]){case'top':pTop+=0;break;case'bottom':pTop+=wnd.height()-this.uiDialog.height();break;default:case'middle':pTop+=(wnd.height()-this.uiDialog.height())/2;}}
pTop=Math.max(pTop,minTop);this.uiDialog.css({top:pTop,left:pLeft});},open:function(){this.overlay=this.options.modal?new $.ui.dialog.overlay(this):null;this.uiDialog.appendTo('body');this.position(this.options.position);this.uiDialog.show();this.moveToTop(true);var openEV=null;var openUI={options:this.options};this.uiDialogTitlebarClose.focus();this.element.triggerHandler("dialogopen",[openEV,openUI],this.options.open);},moveToTop:function(force){if((this.options.modal&&!force)||!this.options.stack){return;}
var maxZ=this.options.zIndex,options=this.options;$('.ui-dialog:visible').each(function(){maxZ=Math.max(maxZ,parseInt($(this).css('z-index'),10)||options.zIndex);});(this.overlay&&this.overlay.$el.css('z-index',++maxZ));this.uiDialog.css('z-index',++maxZ);},close:function(){(this.overlay&&this.overlay.destroy());this.uiDialog.hide();var closeEV=null;var closeUI={options:this.options};this.element.triggerHandler("dialogclose",[closeEV,closeUI],this.options.close);$.ui.dialog.overlay.resize();},destroy:function(){(this.overlay&&this.overlay.destroy());this.uiDialog.hide();this.element.unbind('.dialog').removeData('dialog').removeClass('ui-dialog-content').hide().appendTo('body');this.uiDialog.remove();}});$.extend($.ui.dialog,{defaults:{autoOpen:true,bgiframe:false,buttons:{},closeOnEscape:true,draggable:true,height:200,minHeight:100,minWidth:150,modal:false,overlay:{},position:'center',resizable:true,stack:true,width:300,zIndex:1000},overlay:function(dialog){this.$el=$.ui.dialog.overlay.create(dialog);}});$.extend($.ui.dialog.overlay,{instances:[],events:$.map('focus,mousedown,mouseup,keydown,keypress,click'.split(','),function(e){return e+'.dialog-overlay';}).join(' '),create:function(dialog){if(this.instances.length===0){setTimeout(function(){$('a, :input').bind($.ui.dialog.overlay.events,function(){var allow=false;var $dialog=$(this).parents('.ui-dialog');if($dialog.length){var $overlays=$('.ui-dialog-overlay');if($overlays.length){var maxZ=parseInt($overlays.css('z-index'),10);$overlays.each(function(){maxZ=Math.max(maxZ,parseInt($(this).css('z-index'),10));});allow=parseInt($dialog.css('z-index'),10)>maxZ;}else{allow=true;}}
return allow;});},1);$(document).bind('keydown.dialog-overlay',function(e){var ESC=27;(e.keyCode&&e.keyCode==ESC&&dialog.close());});$(window).bind('resize.dialog-overlay',$.ui.dialog.overlay.resize);}
var $el=$('<div/>').appendTo(document.body).addClass('ui-dialog-overlay').css($.extend({borderWidth:0,margin:0,padding:0,position:'absolute',top:0,left:0,width:this.width(),height:this.height()},dialog.options.overlay));(dialog.options.bgiframe&&$.fn.bgiframe&&$el.bgiframe());this.instances.push($el);return $el;},destroy:function($el){this.instances.splice($.inArray(this.instances,$el),1);if(this.instances.length===0){$('a, :input').add([document,window]).unbind('.dialog-overlay');}
$el.remove();},height:function(){if($.browser.msie&&$.browser.version<7){var scrollHeight=Math.max(document.documentElement.scrollHeight,document.body.scrollHeight);var offsetHeight=Math.max(document.documentElement.offsetHeight,document.body.offsetHeight);if(scrollHeight<offsetHeight){return $(window).height()+'px';}else{return scrollHeight+'px';}}else{return $(document).height()+'px';}},width:function(){if($.browser.msie&&$.browser.version<7){var scrollWidth=Math.max(document.documentElement.scrollWidth,document.body.scrollWidth);var offsetWidth=Math.max(document.documentElement.offsetWidth,document.body.offsetWidth);if(scrollWidth<offsetWidth){return $(window).width()+'px';}else{return scrollWidth+'px';}}else{return $(document).width()+'px';}},resize:function(){var $overlays=$([]);$.each($.ui.dialog.overlay.instances,function(){$overlays=$overlays.add(this);});$overlays.css({width:0,height:0}).css({width:$.ui.dialog.overlay.width(),height:$.ui.dialog.overlay.height()});}});$.extend($.ui.dialog.overlay.prototype,{destroy:function(){$.ui.dialog.overlay.destroy(this.$el);}});})(jQuery);(function($){$.widget("ui.tabs",{init:function(){this.options.event+='.tabs';this.tabify(true);},setData:function(key,value){if((/^selected/).test(key))
this.select(value);else{this.options[key]=value;this.tabify();}},length:function(){return this.$tabs.length;},tabId:function(a){return a.title&&a.title.replace(/\s/g,'_').replace(/[^A-Za-z0-9\-_:\.]/g,'')||this.options.idPrefix+$.data(a);},ui:function(tab,panel){return{options:this.options,tab:tab,panel:panel};},tabify:function(init){this.$lis=$('li:has(a[href])',this.element);this.$tabs=this.$lis.map(function(){return $('a',this)[0];});this.$panels=$([]);var self=this,o=this.options;this.$tabs.each(function(i,a){if(a.hash&&a.hash.replace('#',''))
self.$panels=self.$panels.add(a.hash);else if($(a).attr('href')!='#'){$.data(a,'href.tabs',a.href);$.data(a,'load.tabs',a.href);var id=self.tabId(a);a.href='#'+id;var $panel=$('#'+id);if(!$panel.length){$panel=$(o.panelTemplate).attr('id',id).addClass(o.panelClass).insertAfter(self.$panels[i-1]||self.element);$panel.data('destroy.tabs',true);}
self.$panels=self.$panels.add($panel);}
else
o.disabled.push(i+1);});if(init){this.element.addClass(o.navClass);this.$panels.each(function(){var $this=$(this);$this.addClass(o.panelClass);});if(o.selected===undefined){if(location.hash){this.$tabs.each(function(i,a){if(a.hash==location.hash){o.selected=i;if($.browser.msie||$.browser.opera){var $toShow=$(location.hash),toShowId=$toShow.attr('id');$toShow.attr('id','');setTimeout(function(){$toShow.attr('id',toShowId);},500);}
scrollTo(0,0);return false;}});}
else if(o.cookie){var index=parseInt($.cookie('ui-tabs'+$.data(self.element)),10);if(index&&self.$tabs[index])
o.selected=index;}
else if(self.$lis.filter('.'+o.selectedClass).length)
o.selected=self.$lis.index(self.$lis.filter('.'+o.selectedClass)[0]);}
o.selected=o.selected===null||o.selected!==undefined?o.selected:0;o.disabled=$.unique(o.disabled.concat($.map(this.$lis.filter('.'+o.disabledClass),function(n,i){return self.$lis.index(n);}))).sort();if($.inArray(o.selected,o.disabled)!=-1)
o.disabled.splice($.inArray(o.selected,o.disabled),1);this.$panels.addClass(o.hideClass);this.$lis.removeClass(o.selectedClass);if(o.selected!==null){this.$panels.eq(o.selected).show().removeClass(o.hideClass);this.$lis.eq(o.selected).addClass(o.selectedClass);var onShow=function(){$(self.element).triggerHandler('tabsshow',[self.ui(self.$tabs[o.selected],self.$panels[o.selected])],o.show);};if($.data(this.$tabs[o.selected],'load.tabs'))
this.load(o.selected,onShow);else
onShow();}
$(window).bind('unload',function(){self.$tabs.unbind('.tabs');self.$lis=self.$tabs=self.$panels=null;});}
for(var i=0,li;li=this.$lis[i];i++)
$(li)[$.inArray(i,o.disabled)!=-1&&!$(li).hasClass(o.selectedClass)?'addClass':'removeClass'](o.disabledClass);if(o.cache===false)
this.$tabs.removeData('cache.tabs');var hideFx,showFx,baseFx={'min-width':0,duration:1},baseDuration='normal';if(o.fx&&o.fx.constructor==Array)
hideFx=o.fx[0]||baseFx,showFx=o.fx[1]||baseFx;else
hideFx=showFx=o.fx||baseFx;var resetCSS={display:'',overflow:'',height:''};if(!$.browser.msie)
resetCSS.opacity='';function hideTab(clicked,$hide,$show){$hide.animate(hideFx,hideFx.duration||baseDuration,function(){$hide.addClass(o.hideClass).css(resetCSS);if($.browser.msie&&hideFx.opacity)
$hide[0].style.filter='';if($show)
showTab(clicked,$show,$hide);});}
function showTab(clicked,$show,$hide){if(showFx===baseFx)
$show.css('display','block');$show.animate(showFx,showFx.duration||baseDuration,function(){$show.removeClass(o.hideClass).css(resetCSS);if($.browser.msie&&showFx.opacity)
$show[0].style.filter='';$(self.element).triggerHandler('tabsshow',[self.ui(clicked,$show[0])],o.show);});}
function switchTab(clicked,$li,$hide,$show){$li.addClass(o.selectedClass).siblings().removeClass(o.selectedClass);hideTab(clicked,$hide,$show);}
this.$tabs.unbind('.tabs').bind(o.event,function(){var $li=$(this).parents('li:eq(0)'),$hide=self.$panels.filter(':visible'),$show=$(this.hash);if(($li.hasClass(o.selectedClass)&&!o.unselect)||$li.hasClass(o.disabledClass)||$(this).hasClass(o.loadingClass)||$(self.element).triggerHandler('tabsselect',[self.ui(this,$show[0])],o.select)===false){this.blur();return false;}
self.options.selected=self.$tabs.index(this);if(o.unselect){if($li.hasClass(o.selectedClass)){self.options.selected=null;$li.removeClass(o.selectedClass);self.$panels.stop();hideTab(this,$hide);this.blur();return false;}else if(!$hide.length){self.$panels.stop();var a=this;self.load(self.$tabs.index(this),function(){$li.addClass(o.selectedClass).addClass(o.unselectClass);showTab(a,$show);});this.blur();return false;}}
if(o.cookie)
$.cookie('ui-tabs'+$.data(self.element),self.options.selected,o.cookie);self.$panels.stop();if($show.length){var a=this;self.load(self.$tabs.index(this),$hide.length?function(){switchTab(a,$li,$hide,$show);}:function(){$li.addClass(o.selectedClass);showTab(a,$show);});}else
throw'jQuery UI Tabs: Mismatching fragment identifier.';if($.browser.msie)
this.blur();return false;});if(!(/^click/).test(o.event))
this.$tabs.bind('click.tabs',function(){return false;});},add:function(url,label,index){if(index==undefined)
index=this.$tabs.length;var o=this.options;var $li=$(o.tabTemplate.replace(/#\{href\}/g,url).replace(/#\{label\}/g,label));$li.data('destroy.tabs',true);var id=url.indexOf('#')==0?url.replace('#',''):this.tabId($('a:first-child',$li)[0]);var $panel=$('#'+id);if(!$panel.length){$panel=$(o.panelTemplate).attr('id',id).addClass(o.hideClass).data('destroy.tabs',true);}
$panel.addClass(o.panelClass);if(index>=this.$lis.length){$li.appendTo(this.element);$panel.appendTo(this.element[0].parentNode);}else{$li.insertBefore(this.$lis[index]);$panel.insertBefore(this.$panels[index]);}
o.disabled=$.map(o.disabled,function(n,i){return n>=index?++n:n});this.tabify();if(this.$tabs.length==1){$li.addClass(o.selectedClass);$panel.removeClass(o.hideClass);var href=$.data(this.$tabs[0],'load.tabs');if(href)
this.load(index,href);}
this.element.triggerHandler('tabsadd',[this.ui(this.$tabs[index],this.$panels[index])],o.add);},remove:function(index){var o=this.options,$li=this.$lis.eq(index).remove(),$panel=this.$panels.eq(index).remove();if($li.hasClass(o.selectedClass)&&this.$tabs.length>1)
this.select(index+(index+1<this.$tabs.length?1:-1));o.disabled=$.map($.grep(o.disabled,function(n,i){return n!=index;}),function(n,i){return n>=index?--n:n});this.tabify();this.element.triggerHandler('tabsremove',[this.ui($li.find('a')[0],$panel[0])],o.remove);},enable:function(index){var o=this.options;if($.inArray(index,o.disabled)==-1)
return;var $li=this.$lis.eq(index).removeClass(o.disabledClass);if($.browser.safari){$li.css('display','inline-block');setTimeout(function(){$li.css('display','block');},0);}
o.disabled=$.grep(o.disabled,function(n,i){return n!=index;});this.element.triggerHandler('tabsenable',[this.ui(this.$tabs[index],this.$panels[index])],o.enable);},disable:function(index){var self=this,o=this.options;if(index!=o.selected){this.$lis.eq(index).addClass(o.disabledClass);o.disabled.push(index);o.disabled.sort();this.element.triggerHandler('tabsdisable',[this.ui(this.$tabs[index],this.$panels[index])],o.disable);}},select:function(index){if(typeof index=='string')
index=this.$tabs.index(this.$tabs.filter('[href$='+index+']')[0]);this.$tabs.eq(index).trigger(this.options.event);},load:function(index,callback){var self=this,o=this.options,$a=this.$tabs.eq(index),a=$a[0],bypassCache=callback==undefined||callback===false,url=$a.data('load.tabs');callback=callback||function(){};if(!url||!bypassCache&&$.data(a,'cache.tabs')){callback();return;}
var inner=function(parent){var $parent=$(parent),$inner=$parent.find('*:last');return $inner.length&&$inner||$parent;};var cleanup=function(){self.$tabs.filter('.'+o.loadingClass).removeClass(o.loadingClass).each(function(){if(o.spinner)
inner(this).parent().html(inner(this).data('label.tabs'));});self.xhr=null;};if(o.spinner){var label=inner(a).html();inner(a).wrapInner('<em></em>').find('em').data('label.tabs',label).html(o.spinner);}
var ajaxOptions=$.extend({},o.ajaxOptions,{url:url,success:function(r,s){$(a.hash).html(r);cleanup();if(o.cache)
$.data(a,'cache.tabs',true);$(self.element).triggerHandler('tabsload',[self.ui(self.$tabs[index],self.$panels[index])],o.load);o.ajaxOptions.success&&o.ajaxOptions.success(r,s);callback();}});if(this.xhr){this.xhr.abort();cleanup();}
$a.addClass(o.loadingClass);setTimeout(function(){self.xhr=$.ajax(ajaxOptions);},0);},url:function(index,url){this.$tabs.eq(index).removeData('cache.tabs').data('load.tabs',url);},destroy:function(){var o=this.options;this.element.unbind('.tabs').removeClass(o.navClass).removeData('tabs');this.$tabs.each(function(){var href=$.data(this,'href.tabs');if(href)
this.href=href;var $this=$(this).unbind('.tabs');$.each(['href','load','cache'],function(i,prefix){$this.removeData(prefix+'.tabs');});});this.$lis.add(this.$panels).each(function(){if($.data(this,'destroy.tabs'))
$(this).remove();else
$(this).removeClass([o.selectedClass,o.unselectClass,o.disabledClass,o.panelClass,o.hideClass].join(' '));});}});$.ui.tabs.defaults={unselect:false,event:'click',disabled:[],cookie:null,spinner:'Loading&#8230;',cache:false,idPrefix:'ui-tabs-',ajaxOptions:{},fx:null,tabTemplate:'<li><a href="#{href}"><span>#{label}</span></a></li>',panelTemplate:'<div></div>',navClass:'ui-tabs-nav',selectedClass:'ui-tabs-selected',unselectClass:'ui-tabs-unselect',disabledClass:'ui-tabs-disabled',panelClass:'ui-tabs-panel',hideClass:'ui-tabs-hide',loadingClass:'ui-tabs-loading'};$.ui.tabs.getter="length";$.extend($.ui.tabs.prototype,{rotation:null,rotate:function(ms,continuing){continuing=continuing||false;var self=this,t=this.options.selected;function start(){self.rotation=setInterval(function(){t=++t<self.$tabs.length?t:0;self.select(t);},ms);}
function stop(e){if(!e||e.clientX){clearInterval(self.rotation);}}
if(ms){start();if(!continuing)
this.$tabs.bind(this.options.event,stop);else
this.$tabs.bind(this.options.event,function(){stop();t=self.options.selected;start();});}
else{stop();this.$tabs.unbind(this.options.event,stop);}}});})(jQuery);