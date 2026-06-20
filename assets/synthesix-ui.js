var Mt=Object.defineProperty;var St=Object.getOwnPropertyDescriptor;var l=(o,t,e,s)=>{for(var r=s>1?void 0:s?St(t,e):t,i=o.length-1,a;i>=0;i--)(a=o[i])&&(r=(s?a(t,e,r):a(r))||r);return s&&r&&Mt(t,e,r),r};var F=globalThis,J=F.ShadowRoot&&(F.ShadyCSS===void 0||F.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Y=Symbol(),dt=new WeakMap,N=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==Y)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(J&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=dt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&dt.set(e,t))}return t}toString(){return this.cssText}},ht=o=>new N(typeof o=="string"?o:o+"",void 0,Y),m=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,r,i)=>s+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[i+1],o[0]);return new N(e,o,Y)},ut=(o,t)=>{if(J)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=F.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,o.appendChild(s)}},tt=J?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return ht(e)})(o):o;var{is:Tt,defineProperty:Ot,getOwnPropertyDescriptor:Pt,getOwnPropertyNames:Lt,getOwnPropertySymbols:Ht,getPrototypeOf:Ut}=Object,Z=globalThis,mt=Z.trustedTypes,Nt=mt?mt.emptyScript:"",Rt=Z.reactiveElementPolyfillSupport,R=(o,t)=>o,z={toAttribute(o,t){switch(t){case Boolean:o=o?Nt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},G=(o,t)=>!Tt(o,t),ft={attribute:!0,type:String,converter:z,reflect:!1,useDefault:!1,hasChanged:G};Symbol.metadata??=Symbol("metadata"),Z.litPropertyMetadata??=new WeakMap;var x=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ft){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Ot(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:i}=Pt(this.prototype,t)??{get(){return this[e]},set(a){this[e]=a}};return{get:r,set(a){let c=r?.call(this);i?.call(this,a),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ft}static _$Ei(){if(this.hasOwnProperty(R("elementProperties")))return;let t=Ut(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(R("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(R("properties"))){let e=this.properties,s=[...Lt(e),...Ht(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(tt(r))}else t!==void 0&&e.push(tt(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ut(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:z).toAttribute(e,s.type);this._$Em=t,i==null?this.removeAttribute(r):this.setAttribute(r,i),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let i=s.getPropertyOptions(r),a=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:z;this._$Em=r;let c=a.fromAttribute(e,i.type);this[r]=c??this._$Ej?.get(r)??c,this._$Em=null}}requestUpdate(t,e,s,r=!1,i){if(t!==void 0){let a=this.constructor;if(r===!1&&(i=this[t]),s??=a.getPropertyOptions(t),!((s.hasChanged??G)(i,e)||s.useDefault&&s.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(a._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:i},a){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),i!==!0||a!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,i]of this._$Ep)this[r]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,i]of s){let{wrapped:a}=i,c=this[r];a!==!0||this._$AL.has(r)||c===void 0||this.C(r,void 0,i,c)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[R("elementProperties")]=new Map,x[R("finalized")]=new Map,Rt?.({ReactiveElement:x}),(Z.reactiveElementVersions??=[]).push("2.1.2");var nt=globalThis,gt=o=>o,Q=nt.trustedTypes,vt=Q?Q.createPolicy("lit-html",{createHTML:o=>o}):void 0,At="$lit$",$=`lit$${Math.random().toFixed(9).slice(2)}$`,wt="?"+$,zt=`<${wt}>`,M=document,D=()=>M.createComment(""),q=o=>o===null||typeof o!="object"&&typeof o!="function",lt=Array.isArray,jt=o=>lt(o)||typeof o?.[Symbol.iterator]=="function",et=`[ 	
\f\r]`,j=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,bt=/-->/g,yt=/>/g,k=RegExp(`>|${et}(?:([^\\s"'>=/]+)(${et}*=${et}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),xt=/'/g,_t=/"/g,Et=/^(?:script|style|textarea|title)$/i,ct=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),u=ct(1),Gt=ct(2),Qt=ct(3),S=Symbol.for("lit-noChange"),g=Symbol.for("lit-nothing"),$t=new WeakMap,C=M.createTreeWalker(M,129);function kt(o,t){if(!lt(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return vt!==void 0?vt.createHTML(t):t}var Dt=(o,t)=>{let e=o.length-1,s=[],r,i=t===2?"<svg>":t===3?"<math>":"",a=j;for(let c=0;c<e;c++){let n=o[c],f,b,p=-1,y=0;for(;y<n.length&&(a.lastIndex=y,b=a.exec(n),b!==null);)y=a.lastIndex,a===j?b[1]==="!--"?a=bt:b[1]!==void 0?a=yt:b[2]!==void 0?(Et.test(b[2])&&(r=RegExp("</"+b[2],"g")),a=k):b[3]!==void 0&&(a=k):a===k?b[0]===">"?(a=r??j,p=-1):b[1]===void 0?p=-2:(p=a.lastIndex-b[2].length,f=b[1],a=b[3]===void 0?k:b[3]==='"'?_t:xt):a===_t||a===xt?a=k:a===bt||a===yt?a=j:(a=k,r=void 0);let _=a===k&&o[c+1].startsWith("/>")?" ":"";i+=a===j?n+zt:p>=0?(s.push(f),n.slice(0,p)+At+n.slice(p)+$+_):n+$+(p===-2?c:_)}return[kt(o,i+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},B=class o{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let i=0,a=0,c=t.length-1,n=this.parts,[f,b]=Dt(t,e);if(this.el=o.createElement(f,s),C.currentNode=this.el.content,e===2||e===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(r=C.nextNode())!==null&&n.length<c;){if(r.nodeType===1){if(r.hasAttributes())for(let p of r.getAttributeNames())if(p.endsWith(At)){let y=b[a++],_=r.getAttribute(p).split($),K=/([.?@])?(.*)/.exec(y);n.push({type:1,index:i,name:K[2],strings:_,ctor:K[1]==="."?rt:K[1]==="?"?ot:K[1]==="@"?it:L}),r.removeAttribute(p)}else p.startsWith($)&&(n.push({type:6,index:i}),r.removeAttribute(p));if(Et.test(r.tagName)){let p=r.textContent.split($),y=p.length-1;if(y>0){r.textContent=Q?Q.emptyScript:"";for(let _=0;_<y;_++)r.append(p[_],D()),C.nextNode(),n.push({type:2,index:++i});r.append(p[y],D())}}}else if(r.nodeType===8)if(r.data===wt)n.push({type:2,index:i});else{let p=-1;for(;(p=r.data.indexOf($,p+1))!==-1;)n.push({type:7,index:i}),p+=$.length-1}i++}}static createElement(t,e){let s=M.createElement("template");return s.innerHTML=t,s}};function P(o,t,e=o,s){if(t===S)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,i=q(t)?void 0:t._$litDirective$;return r?.constructor!==i&&(r?._$AO?.(!1),i===void 0?r=void 0:(r=new i(o),r._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=P(o,r._$AS(o,t.values),r,s)),t}var st=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??M).importNode(e,!0);C.currentNode=r;let i=C.nextNode(),a=0,c=0,n=s[0];for(;n!==void 0;){if(a===n.index){let f;n.type===2?f=new V(i,i.nextSibling,this,t):n.type===1?f=new n.ctor(i,n.name,n.strings,this,t):n.type===6&&(f=new at(i,this,t)),this._$AV.push(f),n=s[++c]}a!==n?.index&&(i=C.nextNode(),a++)}return C.currentNode=M,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},V=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=g,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=P(this,t,e),q(t)?t===g||t==null||t===""?(this._$AH!==g&&this._$AR(),this._$AH=g):t!==this._$AH&&t!==S&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):jt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==g&&q(this._$AH)?this._$AA.nextSibling.data=t:this.T(M.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=B.createElement(kt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let i=new st(r,this),a=i.u(this.options);i.p(e),this.T(a),this._$AH=i}}_$AC(t){let e=$t.get(t.strings);return e===void 0&&$t.set(t.strings,e=new B(t)),e}k(t){lt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let i of t)r===e.length?e.push(s=new o(this.O(D()),this.O(D()),this,this.options)):s=e[r],s._$AI(i),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=gt(t).nextSibling;gt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},L=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,i){this.type=1,this._$AH=g,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=g}_$AI(t,e=this,s,r){let i=this.strings,a=!1;if(i===void 0)t=P(this,t,e,0),a=!q(t)||t!==this._$AH&&t!==S,a&&(this._$AH=t);else{let c=t,n,f;for(t=i[0],n=0;n<i.length-1;n++)f=P(this,c[s+n],e,n),f===S&&(f=this._$AH[n]),a||=!q(f)||f!==this._$AH[n],f===g?t=g:t!==g&&(t+=(f??"")+i[n+1]),this._$AH[n]=f}a&&!r&&this.j(t)}j(t){t===g?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},rt=class extends L{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===g?void 0:t}},ot=class extends L{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==g)}},it=class extends L{constructor(t,e,s,r,i){super(t,e,s,r,i),this.type=5}_$AI(t,e=this){if((t=P(this,t,e,0)??g)===S)return;let s=this._$AH,r=t===g&&s!==g||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==g&&(s===g||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},at=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){P(this,t)}};var qt=nt.litHtmlPolyfillSupport;qt?.(B,V),(nt.litHtmlVersions??=[]).push("3.3.3");var Ct=(o,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let i=e?.renderBefore??null;s._$litPart$=r=new V(t.insertBefore(D(),i),i,void 0,e??{})}return r._$AI(o),r};var pt=globalThis,d=class extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Ct(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return S}};d._$litElement$=!0,d.finalized=!0,pt.litElementHydrateSupport?.({LitElement:d});var Bt=pt.litElementPolyfillSupport;Bt?.({LitElement:d});(pt.litElementVersions??=[]).push("4.2.2");var v=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var Vt={attribute:!0,type:String,converter:z,reflect:!1,hasChanged:G},It=(o=Vt,t,e)=>{let{kind:s,metadata:r}=e,i=globalThis.litPropertyMetadata.get(r);if(i===void 0&&globalThis.litPropertyMetadata.set(r,i=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),i.set(e.name,o),s==="accessor"){let{name:a}=e;return{set(c){let n=t.get.call(this);t.set.call(this,c),this.requestUpdate(a,n,o,!0,c)},init(c){return c!==void 0&&this.C(a,void 0,o,c),c}}}if(s==="setter"){let{name:a}=e;return function(c){let n=this[a];t.call(this,c),this.requestUpdate(a,n,o,!0,c)}}throw Error("Unsupported decorator location: "+s)};function h(o){return(t,e)=>typeof e=="object"?It(o,t,e):((s,r,i)=>{let a=r.hasOwnProperty(i);return r.constructor.createProperty(i,s),a?Object.getOwnPropertyDescriptor(r,i):void 0})(o,t,e)}var H=class extends d{constructor(){super(...arguments);this.tone="neutral"}render(){return u`<span class="chip"><slot></slot></span>`}};H.styles=m`
    :host {
      display: inline-flex;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 4px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="info"]) .chip {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .chip {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .chip {
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    :host([tone="muted"]) .chip {
      background: transparent;
    }
  `,l([h({reflect:!0})],H.prototype,"tone",2),H=l([v("sx-chip")],H);var T=class extends d{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(e){e.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return u`
      <article class="card" part="card">
        <div class="body" part="body">
          <div class="head" part="head">
            <slot name="title"></slot>
            <slot name="domain"></slot>
          </div>
          <div class="snippet" part="snippet">
            <slot name="snippet"></slot>
          </div>
          <div class="extra" part="extra">
            <slot name="extra"></slot>
          </div>
          <div class="meta" part="meta">
            <slot name="meta"></slot>
          </div>
        </div>
        <div class="actions" part="actions">
          <slot name="actions"></slot>
        </div>
      </article>
    `}};T.styles=m`
    :host {
      display: block;
      outline: none;
    }

    .card {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--space-4, 16px);
      padding: var(--space-3, 12px) var(--space-4, 16px);
      border: 1px solid var(--line, #cbd5e1);
      border-left: 3px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      transition:
        border-color 120ms ease,
        box-shadow 120ms ease;
    }

    :host([accent="strong"]) .card {
      border-left-color: var(--success, #16a34a);
    }

    :host([accent="good"]) .card {
      border-left-color: var(--accent, #2563eb);
    }

    :host([accent="moderate"]) .card {
      border-left-color: var(--warning, #d97706);
    }

    :host([accent="weak"]) .card {
      border-left-color: var(--line, #cbd5e1);
    }

    :host(:hover) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.08));
    }

    :host(:focus-visible) .card,
    :host(:focus) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .body {
      flex: 1 1 auto;
      min-width: 0;
    }

    .head {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 4px var(--space-3, 12px);
      min-width: 0;
    }

    .snippet {
      margin: 0;
    }

    .extra {
      display: contents;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--space-2, 8px);
    }

    .actions {
      display: flex;
      flex: 0 0 auto;
      align-items: center;
      gap: 6px;
    }

    ::slotted([slot="title"]) {
      color: var(--text, #0f172a);
      font-size: 15px;
      font-weight: 500;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    ::slotted([slot="title"]:hover) {
      color: var(--accent, #2563eb);
      text-decoration: underline;
    }

    ::slotted([slot="domain"]) {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--muted, #64748b);
      font-size: 12px;
    }

    ::slotted([slot="snippet"]) {
      margin: 4px 0 8px;
      color: var(--muted, #64748b);
      font-size: 13px;
      line-height: 1.5;
      overflow-wrap: anywhere;
    }

    @media (max-width: 720px) {
      .card {
        flex-direction: column;
      }

      .actions {
        width: 100%;
      }
    }
  `,l([h({reflect:!0})],T.prototype,"accent",2),l([h({type:Boolean,reflect:!0})],T.prototype,"triage",2),T=l([v("sx-result-card")],T);var O=class extends d{constructor(){super(...arguments);this.level="none";this.expandable=!1}render(){let e=u`<span class="value" part="value"><slot></slot></span>`;return this.expandable?u`
      <details class="score" part="score">
        <summary part="summary">${e}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `:u`<span class="score" part="score">${e}</span>`}};O.styles=m`
    :host {
      display: inline-block;
    }

    .value {
      display: inline-block;
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      font-size: 13px;
      padding: 3px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border: 1px solid var(--line, #cbd5e1);
    }

    :host([level="strong"]) .value {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
      border-color: transparent;
    }

    :host([level="good"]) .value {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
      border-color: transparent;
    }

    :host([level="moderate"]) .value {
      background: var(--warning-soft, #fef3c7);
      color: var(--warning-ink, #92400e);
      border-color: transparent;
    }

    details.score {
      display: inline-block;
    }

    summary {
      list-style: none;
      cursor: pointer;
    }

    summary::-webkit-details-marker {
      display: none;
    }

    summary:focus-visible .value {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .list {
      margin: 8px 0 4px;
      padding-left: 18px;
      font-size: 12px;
      color: var(--muted, #64748b);
    }

    .note {
      display: block;
      font-size: 11px;
      color: var(--muted, #64748b);
    }

    ::slotted([slot="note"]) {
      color: var(--muted, #64748b);
    }
  `,l([h({reflect:!0})],O.prototype,"level",2),l([h({type:Boolean,reflect:!0})],O.prototype,"expandable",2),O=l([v("sx-score")],O);var A=class extends d{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return u`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?u`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};A.styles=m`
    :host {
      display: inline-flex;
    }
    .tag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 3px 8px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="neutral"]) .tag {
      color: var(--text, #0f172a);
    }
    :host([tone="info"]) .tag {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .tag {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .tag {
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    .remove {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 14px;
      height: 14px;
      margin-right: -2px;
      padding: 0;
      border: none;
      border-radius: 50%;
      background: transparent;
      color: inherit;
      font: inherit;
      line-height: 1;
      cursor: pointer;
      opacity: 0.7;
    }
    .remove:hover {
      opacity: 1;
      background: color-mix(in srgb, currentColor 18%, transparent);
    }
    .remove:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
  `,l([h({reflect:!0})],A.prototype,"tone",2),l([h({type:Boolean,reflect:!0})],A.prototype,"removable",2),l([h({attribute:"remove-label"})],A.prototype,"removeLabel",2),A=l([v("sx-tag")],A);var I=class extends d{render(){return u`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};I.styles=m`
    :host {
      display: inline-flex;
    }
    .provenance {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: var(--muted, #64748b);
      min-width: 0;
    }
    .detail {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    ::slotted([slot="icon"]) {
      width: 0.95em;
      height: 0.95em;
      flex: 0 0 auto;
    }
  `,I=l([v("sx-provenance")],I);var U=class extends d{constructor(){super(...arguments);this.status="pending"}render(){return u`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`}};U.styles=m`
    :host {
      display: inline-flex;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--muted, #64748b);
    }
    :host([status="verified"]) .badge {
      color: var(--success-ink, #166534);
    }
    :host([status="error"]) .badge {
      color: var(--danger, #dc2626);
    }
  `,l([h({reflect:!0})],U.prototype,"status",2),U=l([v("sx-evidence-badge")],U);var w=class extends d{constructor(){super(...arguments);this.selected="";this.pane="list";this.backLabel="Back to list"}get _items(){return Array.from(this.querySelectorAll("[data-inspector-item]"))}get _panels(){return Array.from(this.querySelectorAll("[data-inspector-panel]"))}_valueOf(e){return e.getAttribute("data-inspector-item")??""}firstUpdated(){if(!this.selected){let e=this._items[0];e&&(this.selected=this._valueOf(e))}this._sync()}updated(e){e.has("selected")&&this._sync()}_sync(){let e=this.selected;for(let s of this._items)this._valueOf(s)===e?s.setAttribute("aria-current","true"):s.removeAttribute("aria-current");for(let s of this._panels)s.hidden=s.getAttribute("data-inspector-panel")!==e}_select(e,s=!1){if(e===this.selected){this.pane="detail";return}let r=this.selected;this.selected=e,this.pane="detail",this.dispatchEvent(new CustomEvent("sx-inspector-select",{detail:{value:e,previous:r},bubbles:!0,composed:!0})),s&&this.updateComplete.then(()=>{this._items.find(a=>this._valueOf(a)===e)?.focus()})}_onListClick(e){let r=e.target?.closest("[data-inspector-item]");r&&this.contains(r)&&this._select(this._valueOf(r))}_onListKeydown(e){if(!["ArrowDown","ArrowUp","Home","End"].includes(e.key))return;let r=this._items;if(!r.length)return;let i=r.findIndex(c=>this._valueOf(c)===this.selected),a=i;e.key==="ArrowDown"?a=Math.min(r.length-1,i+1):e.key==="ArrowUp"?a=Math.max(0,i-1):e.key==="Home"?a=0:e.key==="End"&&(a=r.length-1),a!==i&&(e.preventDefault(),this._select(this._valueOf(r[a]),!0))}_onBack(){this.pane="list",this.updateComplete.then(()=>{this._items.find(s=>this._valueOf(s)===this.selected)?.focus()})}_onSlotChange(){if(!this.selected){let e=this._items[0];if(e){this.selected=e.getAttribute("data-inspector-item")??"";return}}this._sync()}render(){return u`
      <div class="frame" part="frame">
        <div class="list" part="list">
          <div class="header" part="list-header"><slot name="list-header"></slot></div>
          <div
            class="list-body"
            @click=${this._onListClick}
            @keydown=${this._onListKeydown}
          >
            <slot name="list" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
        <div class="detail" part="detail">
          <div class="detail-header" part="detail-header">
            <button
              class="back"
              part="back"
              type="button"
              aria-label=${this.backLabel}
              @click=${this._onBack}
            >
              ‹ <slot name="back-label">Back</slot>
            </button>
            <div class="header"><slot name="detail-header"></slot></div>
          </div>
          <div class="detail-body" part="detail-body">
            <slot name="detail" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
      </div>
    `}};w.styles=m`
    :host {
      display: block;
    }
    .frame {
      display: grid;
      grid-template-columns: minmax(220px, 320px) 1fr;
      gap: var(--space-4, 16px);
      align-items: start;
    }
    .list {
      display: flex;
      flex-direction: column;
      gap: var(--space-2, 8px);
      min-width: 0;
    }
    .list-body {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 0;
      max-height: var(--sx-inspector-list-h, 70vh);
      overflow: auto;
    }
    .detail {
      min-width: 0;
    }
    .detail-header {
      display: flex;
      align-items: center;
      gap: var(--space-2, 8px);
      margin-bottom: var(--space-2, 8px);
    }
    .detail-header:empty {
      display: none;
    }
    .header {
      font-size: 13px;
      font-weight: 600;
      color: var(--muted, #64748b);
    }
    .back {
      display: none;
      align-items: center;
      gap: 4px;
      font: inherit;
      font-size: 13px;
      padding: 4px 8px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      cursor: pointer;
    }
    .back:hover {
      border-color: var(--accent, #2563eb);
    }
    .back:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
    ::slotted([data-inspector-item]) {
      cursor: pointer;
    }
    @media (max-width: 720px) {
      .frame {
        grid-template-columns: 1fr;
      }
      :host([pane="list"]) .detail {
        display: none;
      }
      :host([pane="detail"]) .list {
        display: none;
      }
      .back {
        display: inline-flex;
      }
    }
  `,l([h({reflect:!0})],w.prototype,"selected",2),l([h({reflect:!0})],w.prototype,"pane",2),l([h({attribute:"back-label"})],w.prototype,"backLabel",2),w=l([v("sx-inspector")],w);var E=class extends d{constructor(){super(...arguments);this.kind="";this.confidence="";this.status="candidate"}_onOptionalSlot(e){let s=e.target,r=s.parentElement;if(!r)return;let i=s.assignedNodes({flatten:!0}).some(a=>a.nodeType===Node.ELEMENT_NODE||(a.textContent??"").trim().length>0);r.hidden=!i}render(){return u`
      <article class="entity" part="entity">
        <div class="head" part="head">
          <span class="kind" part="kind">${this.kind}</span>
          ${this.confidence?u`<span class="confidence" part="confidence">${this.confidence}</span>`:null}
          <span class="actions" part="actions"><slot name="actions"></slot></span>
        </div>
        <div class="value" part="value"><slot></slot></div>
        <div class="meta" part="meta" hidden>
          <slot name="meta" @slotchange=${this._onOptionalSlot}></slot>
        </div>
        <div class="properties" part="properties" hidden>
          <slot name="properties" @slotchange=${this._onOptionalSlot}></slot>
        </div>
      </article>
    `}};E.styles=m`
    :host {
      display: block;
    }
    .entity {
      padding: 12px 14px;
      border: 1px solid var(--line, #cbd5e1);
      border-left: 4px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
    }
    :host([status="confirmed"]) .entity {
      border-left-color: var(--secondary, #06b6d4);
    }
    :host([status="rejected"]) .entity {
      opacity: 0.65;
    }
    .head {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .kind {
      color: var(--secondary, #06b6d4);
      font-size: 12px;
      font-weight: 700;
      text-transform: capitalize;
    }
    .confidence {
      color: var(--muted, #64748b);
      font-size: 11px;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-left: auto;
    }
    .value {
      margin-top: 4px;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 13px;
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .meta[hidden],
    .properties[hidden] {
      display: none;
    }
    .meta:not([hidden]),
    .properties:not([hidden]) {
      margin-top: 8px;
    }
    .properties {
      display: grid;
      gap: 4px;
    }
  `,l([h()],E.prototype,"kind",2),l([h()],E.prototype,"confidence",2),l([h({reflect:!0})],E.prototype,"status",2),E=l([v("sx-entity")],E);var W=class extends d{render(){return u`<div class="property" part="property">
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="value" part="value"><slot></slot></span>
      <span class="actions" part="actions"><slot name="actions"></slot></span>
    </div>`}};W.styles=m`
    :host {
      display: block;
    }
    .property {
      display: grid;
      grid-template-columns: minmax(100px, auto) minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      font-size: 13px;
    }
    .label {
      color: var(--secondary, #06b6d4);
      text-transform: capitalize;
      overflow-wrap: anywhere;
    }
    .value {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    @media (max-width: 540px) {
      .property {
        grid-template-columns: 1fr auto;
      }
      .label {
        grid-column: 1 / -1;
      }
    }
  `,W=l([v("sx-property")],W);
