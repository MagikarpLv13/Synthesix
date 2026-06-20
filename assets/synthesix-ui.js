var kt=Object.defineProperty;var Ct=Object.getOwnPropertyDescriptor;var c=(i,t,e,s)=>{for(var r=s>1?void 0:s?Ct(t,e):t,o=i.length-1,n;o>=0;o--)(n=i[o])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&kt(t,e,r),r};var W=globalThis,K=W.ShadowRoot&&(W.ShadyCSS===void 0||W.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Q=Symbol(),ct=new WeakMap,L=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==Q)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(K&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ct.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ct.set(e,t))}return t}toString(){return this.cssText}},dt=i=>new L(typeof i=="string"?i:i+"",void 0,Q),v=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,r,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[o+1],i[0]);return new L(e,i,Q)},pt=(i,t)=>{if(K)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=W.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}},X=K?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return dt(e)})(i):i;var{is:St,defineProperty:Mt,getOwnPropertyDescriptor:Pt,getOwnPropertyNames:Ot,getOwnPropertySymbols:Ht,getPrototypeOf:Tt}=Object,F=globalThis,ht=F.trustedTypes,Ut=ht?ht.emptyScript:"",Lt=F.reactiveElementPolyfillSupport,N=(i,t)=>i,R={toAttribute(i,t){switch(t){case Boolean:i=i?Ut:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},J=(i,t)=>!St(i,t),ut={attribute:!0,type:String,converter:R,reflect:!1,useDefault:!1,hasChanged:J};Symbol.metadata??=Symbol("metadata"),F.litPropertyMetadata??=new WeakMap;var _=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ut){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Mt(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:o}=Pt(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let l=r?.call(this);o?.call(this,n),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ut}static _$Ei(){if(this.hasOwnProperty(N("elementProperties")))return;let t=Tt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(N("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(N("properties"))){let e=this.properties,s=[...Ot(e),...Ht(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(X(r))}else t!==void 0&&e.push(X(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return pt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:R).toAttribute(e,s.type);this._$Em=t,o==null?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let o=s.getPropertyOptions(r),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:R;this._$Em=r;let l=n.fromAttribute(e,o.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,o){if(t!==void 0){let n=this.constructor;if(r===!1&&(o=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??J)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:o},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),o!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,o]of this._$Ep)this[r]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,o]of s){let{wrapped:n}=o,l=this[r];n!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,o,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};_.elementStyles=[],_.shadowRootOptions={mode:"open"},_[N("elementProperties")]=new Map,_[N("finalized")]=new Map,Lt?.({ReactiveElement:_}),(F.reactiveElementVersions??=[]).push("2.1.2");var ot=globalThis,mt=i=>i,Z=ot.trustedTypes,ft=Z?Z.createPolicy("lit-html",{createHTML:i=>i}):void 0,$t="$lit$",x=`lit$${Math.random().toFixed(9).slice(2)}$`,xt="?"+x,Nt=`<${xt}>`,C=document,z=()=>C.createComment(""),D=i=>i===null||typeof i!="object"&&typeof i!="function",nt=Array.isArray,Rt=i=>nt(i)||typeof i?.[Symbol.iterator]=="function",Y=`[ 	
\f\r]`,j=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,gt=/-->/g,vt=/>/g,w=RegExp(`>|${Y}(?:([^\\s"'>=/]+)(${Y}*=${Y}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),bt=/'/g,yt=/"/g,At=/^(?:script|style|textarea|title)$/i,at=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),f=at(1),Jt=at(2),Zt=at(3),S=Symbol.for("lit-noChange"),m=Symbol.for("lit-nothing"),_t=new WeakMap,k=C.createTreeWalker(C,129);function Et(i,t){if(!nt(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ft!==void 0?ft.createHTML(t):t}var jt=(i,t)=>{let e=i.length-1,s=[],r,o=t===2?"<svg>":t===3?"<math>":"",n=j;for(let l=0;l<e;l++){let a=i[l],u,g,d=-1,y=0;for(;y<a.length&&(n.lastIndex=y,g=n.exec(a),g!==null);)y=n.lastIndex,n===j?g[1]==="!--"?n=gt:g[1]!==void 0?n=vt:g[2]!==void 0?(At.test(g[2])&&(r=RegExp("</"+g[2],"g")),n=w):g[3]!==void 0&&(n=w):n===w?g[0]===">"?(n=r??j,d=-1):g[1]===void 0?d=-2:(d=n.lastIndex-g[2].length,u=g[1],n=g[3]===void 0?w:g[3]==='"'?yt:bt):n===yt||n===bt?n=w:n===gt||n===vt?n=j:(n=w,r=void 0);let $=n===w&&i[l+1].startsWith("/>")?" ":"";o+=n===j?a+Nt:d>=0?(s.push(u),a.slice(0,d)+$t+a.slice(d)+x+$):a+x+(d===-2?l:$)}return[Et(i,o+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},q=class i{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let o=0,n=0,l=t.length-1,a=this.parts,[u,g]=jt(t,e);if(this.el=i.createElement(u,s),k.currentNode=this.el.content,e===2||e===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(r=k.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let d of r.getAttributeNames())if(d.endsWith($t)){let y=g[n++],$=r.getAttribute(d).split(x),I=/([.?@])?(.*)/.exec(y);a.push({type:1,index:o,name:I[2],strings:$,ctor:I[1]==="."?et:I[1]==="?"?st:I[1]==="@"?rt:H}),r.removeAttribute(d)}else d.startsWith(x)&&(a.push({type:6,index:o}),r.removeAttribute(d));if(At.test(r.tagName)){let d=r.textContent.split(x),y=d.length-1;if(y>0){r.textContent=Z?Z.emptyScript:"";for(let $=0;$<y;$++)r.append(d[$],z()),k.nextNode(),a.push({type:2,index:++o});r.append(d[y],z())}}}else if(r.nodeType===8)if(r.data===xt)a.push({type:2,index:o});else{let d=-1;for(;(d=r.data.indexOf(x,d+1))!==-1;)a.push({type:7,index:o}),d+=x.length-1}o++}}static createElement(t,e){let s=C.createElement("template");return s.innerHTML=t,s}};function O(i,t,e=i,s){if(t===S)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,o=D(t)?void 0:t._$litDirective$;return r?.constructor!==o&&(r?._$AO?.(!1),o===void 0?r=void 0:(r=new o(i),r._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=O(i,r._$AS(i,t.values),r,s)),t}var tt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??C).importNode(e,!0);k.currentNode=r;let o=k.nextNode(),n=0,l=0,a=s[0];for(;a!==void 0;){if(n===a.index){let u;a.type===2?u=new B(o,o.nextSibling,this,t):a.type===1?u=new a.ctor(o,a.name,a.strings,this,t):a.type===6&&(u=new it(o,this,t)),this._$AV.push(u),a=s[++l]}n!==a?.index&&(o=k.nextNode(),n++)}return k.currentNode=C,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},B=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=m,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=O(this,t,e),D(t)?t===m||t==null||t===""?(this._$AH!==m&&this._$AR(),this._$AH=m):t!==this._$AH&&t!==S&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Rt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==m&&D(this._$AH)?this._$AA.nextSibling.data=t:this.T(C.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=q.createElement(Et(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let o=new tt(r,this),n=o.u(this.options);o.p(e),this.T(n),this._$AH=o}}_$AC(t){let e=_t.get(t.strings);return e===void 0&&_t.set(t.strings,e=new q(t)),e}k(t){nt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let o of t)r===e.length?e.push(s=new i(this.O(z()),this.O(z()),this,this.options)):s=e[r],s._$AI(o),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=mt(t).nextSibling;mt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},H=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,o){this.type=1,this._$AH=m,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=m}_$AI(t,e=this,s,r){let o=this.strings,n=!1;if(o===void 0)t=O(this,t,e,0),n=!D(t)||t!==this._$AH&&t!==S,n&&(this._$AH=t);else{let l=t,a,u;for(t=o[0],a=0;a<o.length-1;a++)u=O(this,l[s+a],e,a),u===S&&(u=this._$AH[a]),n||=!D(u)||u!==this._$AH[a],u===m?t=m:t!==m&&(t+=(u??"")+o[a+1]),this._$AH[a]=u}n&&!r&&this.j(t)}j(t){t===m?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},et=class extends H{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===m?void 0:t}},st=class extends H{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==m)}},rt=class extends H{constructor(t,e,s,r,o){super(t,e,s,r,o),this.type=5}_$AI(t,e=this){if((t=O(this,t,e,0)??m)===S)return;let s=this._$AH,r=t===m&&s!==m||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==m&&(s===m||r);r&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},it=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){O(this,t)}};var zt=ot.litHtmlPolyfillSupport;zt?.(q,B),(ot.litHtmlVersions??=[]).push("3.3.3");var wt=(i,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let o=e?.renderBefore??null;s._$litPart$=r=new B(t.insertBefore(z(),o),o,void 0,e??{})}return r._$AI(i),r};var lt=globalThis,p=class extends _{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=wt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return S}};p._$litElement$=!0,p.finalized=!0,lt.litElementHydrateSupport?.({LitElement:p});var Dt=lt.litElementPolyfillSupport;Dt?.({LitElement:p});(lt.litElementVersions??=[]).push("4.2.2");var b=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var qt={attribute:!0,type:String,converter:R,reflect:!1,hasChanged:J},Bt=(i=qt,t,e)=>{let{kind:s,metadata:r}=e,o=globalThis.litPropertyMetadata.get(r);if(o===void 0&&globalThis.litPropertyMetadata.set(r,o=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),o.set(e.name,i),s==="accessor"){let{name:n}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,a,i,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,i,l),l}}}if(s==="setter"){let{name:n}=e;return function(l){let a=this[n];t.call(this,l),this.requestUpdate(n,a,i,!0,l)}}throw Error("Unsupported decorator location: "+s)};function h(i){return(t,e)=>typeof e=="object"?Bt(i,t,e):((s,r,o)=>{let n=r.hasOwnProperty(o);return r.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(r,o):void 0})(i,t,e)}var T=class extends p{constructor(){super(...arguments);this.tone="neutral"}render(){return f`<span class="chip"><slot></slot></span>`}};T.styles=v`
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
  `,c([h({reflect:!0})],T.prototype,"tone",2),T=c([b("sx-chip")],T);var M=class extends p{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(e){e.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return f`
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
    `}};M.styles=v`
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
  `,c([h({reflect:!0})],M.prototype,"accent",2),c([h({type:Boolean,reflect:!0})],M.prototype,"triage",2),M=c([b("sx-result-card")],M);var P=class extends p{constructor(){super(...arguments);this.level="none";this.expandable=!1}render(){let e=f`<span class="value" part="value"><slot></slot></span>`;return this.expandable?f`
      <details class="score" part="score">
        <summary part="summary">${e}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `:f`<span class="score" part="score">${e}</span>`}};P.styles=v`
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
  `,c([h({reflect:!0})],P.prototype,"level",2),c([h({type:Boolean,reflect:!0})],P.prototype,"expandable",2),P=c([b("sx-score")],P);var A=class extends p{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return f`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?f`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};A.styles=v`
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
  `,c([h({reflect:!0})],A.prototype,"tone",2),c([h({type:Boolean,reflect:!0})],A.prototype,"removable",2),c([h({attribute:"remove-label"})],A.prototype,"removeLabel",2),A=c([b("sx-tag")],A);var V=class extends p{render(){return f`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};V.styles=v`
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
  `,V=c([b("sx-provenance")],V);var U=class extends p{constructor(){super(...arguments);this.status="pending"}render(){return f`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`}};U.styles=v`
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
  `,c([h({reflect:!0})],U.prototype,"status",2),U=c([b("sx-evidence-badge")],U);var E=class extends p{constructor(){super(...arguments);this.selected="";this.pane="list";this.backLabel="Back to list"}get _items(){return Array.from(this.querySelectorAll("[data-inspector-item]"))}get _panels(){return Array.from(this.querySelectorAll("[data-inspector-panel]"))}_valueOf(e){return e.getAttribute("data-inspector-item")??""}firstUpdated(){if(!this.selected){let e=this._items[0];e&&(this.selected=this._valueOf(e))}this._sync()}updated(e){e.has("selected")&&this._sync()}_sync(){let e=this.selected;for(let s of this._items)this._valueOf(s)===e?s.setAttribute("aria-current","true"):s.removeAttribute("aria-current");for(let s of this._panels)s.hidden=s.getAttribute("data-inspector-panel")!==e}_select(e,s=!1){if(e===this.selected){this.pane="detail";return}let r=this.selected;this.selected=e,this.pane="detail",this.dispatchEvent(new CustomEvent("sx-inspector-select",{detail:{value:e,previous:r},bubbles:!0,composed:!0})),s&&this.updateComplete.then(()=>{this._items.find(n=>this._valueOf(n)===e)?.focus()})}_onListClick(e){let r=e.target?.closest("[data-inspector-item]");r&&this.contains(r)&&this._select(this._valueOf(r))}_onListKeydown(e){if(!["ArrowDown","ArrowUp","Home","End"].includes(e.key))return;let r=this._items;if(!r.length)return;let o=r.findIndex(l=>this._valueOf(l)===this.selected),n=o;e.key==="ArrowDown"?n=Math.min(r.length-1,o+1):e.key==="ArrowUp"?n=Math.max(0,o-1):e.key==="Home"?n=0:e.key==="End"&&(n=r.length-1),n!==o&&(e.preventDefault(),this._select(this._valueOf(r[n]),!0))}_onBack(){this.pane="list",this.updateComplete.then(()=>{this._items.find(s=>this._valueOf(s)===this.selected)?.focus()})}_onSlotChange(){if(!this.selected){let e=this._items[0];if(e){this.selected=e.getAttribute("data-inspector-item")??"";return}}this._sync()}render(){return f`
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
    `}};E.styles=v`
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
  `,c([h({reflect:!0})],E.prototype,"selected",2),c([h({reflect:!0})],E.prototype,"pane",2),c([h({attribute:"back-label"})],E.prototype,"backLabel",2),E=c([b("sx-inspector")],E);
