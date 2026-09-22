/* ===========================================================================
   Agentic AI & AI-Assisted Development with GitHub Copilot - slide runner,
   shared by every deck in this course.
   Plain DOM, no dependencies, no CDN. Works from file:// and offline.

   A deck authors only <section class="slide"> blocks inside #viewport/#stage,
   with data-sec, data-title, data-notes, data-tier (K|D|R) and optionally
   data-after="lab", and names itself with <body data-deck="Module N">.
   Header eyebrow, footer, progress bar, HUD, index and notes are built here.

   Keys:  arrows / space / PgUp / PgDn / Home / End  navigate
          k / K  next / previous slide on the key path (skips R, and after-lab
                 slides until L is on)      L  after-lab slides on / off
          O index      N notes      F fullscreen      Esc close
   =========================================================================== */
(function(){
  var BRAND={org:'Gheware DevOps &amp; Agentic AI',site:'devops.gheware.com',siteU:'https://devops.gheware.com',
    mail:'training@gheware.com',phone:'+91-9606795215',trainer:'Rajesh Gheware'};
  var DECK=document.body.dataset.deck||'Agentic ADLC';
  var slides=[].slice.call(document.querySelectorAll('.slide'));
  var stage=document.getElementById('stage'),viewport=document.getElementById('viewport');
  function el(h){var t=document.createElement('div');t.innerHTML=h;return t.firstChild;}

  // ---- index and notes overlays ----
  document.body.appendChild(el('<div id="toc"><h3>'+DECK+' &mdash; slide index</h3>'+
    '<p class="hint">click a slide, or press O to close &middot; K key &middot; D demo &middot; R reference</p>'+
    '<div class="cols" id="toclist"></div></div>'));
  document.body.appendChild(el('<div id="notes"><div class="h">NOTES &mdash; MORE ON THIS SLIDE</div><div id="notesbody"></div></div>'));
  var toc=document.getElementById('toc'),notes=document.getElementById('notes'),notesBody=document.getElementById('notesbody');

  // ---- chrome: progress bar and HUD ----
  document.body.appendChild(el('<div id="bar"><i></i></div>'));
  document.body.appendChild(el(
    '<div id="hud">'+
      '<a href="../course-outline-3day-onepager.html" title="Open the 3-day course outline">OUTLINE</a><span class="sep">|</span>'+
      '<a href="#" data-act="index" title="Index (O)">index</a><span class="sep">|</span>'+
      '<a href="#" data-act="notes" title="Notes on this slide (N)">notes</a><span class="sep">|</span>'+
      '<span class="lab" id="lab" title="L toggles after-lab slides on the key path"></span><span class="sep">|</span>'+
      '<span class="tier" id="tier"></span><span class="after" id="after">AFTER LAB</span>'+
      '<span id="num"></span>'+
    '</div>'));
  var elBar=document.querySelector('#bar > i'),elNum=document.getElementById('num');
  var elTier=document.getElementById('tier'),elAfter=document.getElementById('after'),elLab=document.getElementById('lab');

  // ---- header (eyebrow from data-sec) and footer on every slide ----
  slides.forEach(function(s){
    var h2=s.querySelector(':scope > h2');
    if(h2){
      var hd=el('<header><div class="hgroup"><p class="eyebrow">'+(s.dataset.sec||'')+'</p></div></header>');
      s.insertBefore(hd,h2);hd.firstChild.appendChild(h2);
    }
    var f=document.createElement('footer');
    f.innerHTML='<span class="brand"><b>'+BRAND.org+'</b> &middot; <a href="'+BRAND.siteU+'">'+BRAND.site+'</a> &middot; '+
      BRAND.mail+' &middot; '+BRAND.phone+'</span><span>'+DECK+' &middot; Trainer: '+BRAND.trainer+'</span>';
    s.appendChild(f);
  });

  // The key path skips reference slides, and skips after-lab slides until the lab is scored.
  var postLab=false;
  function onPath(n){var s=slides[n];return s.dataset.tier!=='R'&&(postLab||!s.dataset.after);}
  function paintLab(){elLab.innerHTML='L '+(postLab?'<b>ON</b>':'off');}
  var i=0;

  // ---- build the index, grouped by section ----
  var list=document.getElementById('toclist'),grp=null,last=null;
  slides.forEach(function(s,k){
    var sec=s.dataset.sec||'';
    if(sec!==last){
      grp=document.createElement('div');grp.className='grp';
      var h=document.createElement('div');h.className='grph';h.innerHTML=sec;grp.appendChild(h);
      list.appendChild(grp);last=sec;
    }
    var a=document.createElement('a');a.href='#'+(k+1);
    var tr=s.dataset.tier||'R';
    a.innerHTML='<span class="n">'+(k+1<10?'0':'')+(k+1)+'</span><span class="tg '+tr+'">'+tr+'</span>'+(s.dataset.title||'');
    if(s.dataset.after)a.className='aft';
    a.onclick=function(e){e.preventDefault();go(k);toc.classList.remove('on');};
    grp.appendChild(a);
  });
  var links=[].slice.call(toc.querySelectorAll('a'));

  // ---- fit each slide's body to its space (as in the python-accelerated runner) ----
  // Sparse slides grow, dense ones shrink a little. Measured once per slide, when first shown.
  var FIT_MIN=0.8,FIT_MAX=1.15;
  function overflowing(sl){
    if(sl.scrollHeight>sl.clientHeight+1||sl.scrollWidth>sl.clientWidth+1)return true;
    var box=sl.getBoundingClientRect(),foot=sl.querySelector(':scope > footer');
    if(foot&&foot.getBoundingClientRect().bottom>box.bottom+1)return true;
    var b=sl.querySelector(':scope > .body');
    if(b&&(b.scrollHeight>b.clientHeight+1||b.scrollWidth>b.clientWidth+1))return true;
    var files=sl.querySelectorAll('.file');
    for(var j=0;j<files.length;j++)if(files[j].scrollWidth>files[j].clientWidth+1)return true;
    return false;
  }
  function fitSlide(sl){
    var body=sl.querySelector(':scope > .body');
    if(!body||sl.getAttribute('data-fitted'))return;
    var lo=FIT_MIN,hi=FIT_MAX;
    body.style.zoom=hi;
    if(overflowing(sl)){
      for(var k=0;k<9;k++){var mid=(lo+hi)/2;body.style.zoom=mid;if(overflowing(sl))hi=mid;else lo=mid;}
      body.style.zoom=lo;
    }
    var z=parseFloat(body.style.zoom)*0.97;body.style.zoom=z;
    while(overflowing(sl)&&z>FIT_MIN){z=Math.max(FIT_MIN,z-0.03);body.style.zoom=z;}
    sl.setAttribute('data-fitted',body.style.zoom);
  }

  function go(n){
    i=Math.max(0,Math.min(slides.length-1,n));
    slides.forEach(function(s,k){s.classList.toggle('active',k===i);});
    fitSlide(slides[i]);
    links.forEach(function(a,k){a.classList.toggle('cur',k===i);});
    elNum.textContent=(i+1)+' / '+slides.length;
    var tr=slides[i].dataset.tier||'R';
    elTier.className='tier '+tr;elTier.textContent=(tr==='D'?'DEMO':tr==='K'?'KEY':'REF');
    elAfter.classList.toggle('on',!!slides[i].dataset.after);
    elBar.style.width=((i+1)/slides.length*100)+'%';
    notesBody.textContent=slides[i].dataset.notes||'No notes for this slide.';
    if(history.replaceState)history.replaceState(null,'','#'+(i+1));
  }
  function fit(){
    var extra=notes.classList.contains('on')?notes.offsetHeight:0;
    viewport.style.bottom=extra+'px';
    var s=Math.min(window.innerWidth/1280,(window.innerHeight-extra)/720);
    stage.style.transform='scale('+s+')';
  }
  function toggleNotes(){notes.classList.toggle('on');fit();}
  document.getElementById('hud').addEventListener('click',function(e){
    var act=e.target.getAttribute('data-act');if(!act)return;
    e.preventDefault();
    if(act==='index')toc.classList.toggle('on');else toggleNotes();
  });
  toc.addEventListener('click',function(e){if(e.target===toc)toc.classList.remove('on');});
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    var k=e.key;
    if(k==='ArrowRight'||k==='PageDown'||k===' '){go(i+1);e.preventDefault();}
    else if(k==='ArrowLeft'||k==='PageUp'||k==='p'){go(i-1);e.preventDefault();}
    else if(k==='Home'){go(0);}
    else if(k==='End'){go(slides.length-1);}
    else if(k==='o'||k==='O'){toc.classList.toggle('on');}
    else if(k==='n'||k==='N'){toggleNotes();}
    else if(k==='f'||k==='F'){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen();}
    else if(k==='k'){for(var j=i+1;j<slides.length;j++){if(onPath(j)){go(j);break;}}}
    else if(k==='K'){for(var j2=i-1;j2>=0;j2--){if(onPath(j2)){go(j2);break;}}}
    else if(k==='l'||k==='L'){postLab=!postLab;paintLab();}
    else if(k==='Escape'){toc.classList.remove('on');notes.classList.remove('on');fit();}
  });
  // click / swipe on the stage
  var x0=null;
  stage.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;},{passive:true});
  stage.addEventListener('touchend',function(e){
    if(x0===null)return;var dx=e.changedTouches[0].clientX-x0;
    if(Math.abs(dx)>45)go(i+(dx<0?1:-1));x0=null;
  },{passive:true});
  window.addEventListener('hashchange',function(){
    var n=parseInt(location.hash.replace('#',''),10);if(n)go(n-1);
  });
  fit();
  paintLab();
  var start=parseInt(location.hash.replace('#',''),10);
  go(start?start-1:0);

  // a fit measured before the final font is in use is wrong: measure again
  function refit(){slides.forEach(function(s){s.removeAttribute('data-fitted');});fitSlide(slides[i]);}
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(refit);
  window.addEventListener('load',refit);
  var rt;window.addEventListener('resize',function(){fit();clearTimeout(rt);rt=setTimeout(refit,150);});
})();
