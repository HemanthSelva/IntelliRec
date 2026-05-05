import streamlit as st
from auth.session import signup_user, init_session, login_with_google

# ── Google Font import ─────────────────────────────────────────────────────────
_FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:'
    'wght@400;500;600;700;800&display=swap" rel="stylesheet">'
)

# ── Compact CSS ────────────────────────────────────────────────────────────────
_CSS = """<style>
/* ── Force light page background (overrides config.toml base=dark) ── */
html,body{background:#f4f6fb!important}
.stApp,[data-testid="stAppViewContainer"]{background:#f4f6fb!important}
/* ── Base reset ── */
*,*::before,*::after{box-sizing:border-box}
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif!important}
[data-testid="stAppViewContainer"]>.main{
  background:linear-gradient(135deg,#EEF2FF 0%,#F0FDFF 50%,#F5F3FF 100%)!important}

/* ── Left column glass ── */
[data-testid="column"]:nth-of-type(1){
  background:rgba(255,255,255,0.88)!important;
  backdrop-filter:blur(24px)!important;
  -webkit-backdrop-filter:blur(24px)!important;
  border-right:1px solid rgba(255,255,255,0.5)!important;
  box-shadow:4px 0 30px rgba(108,99,255,0.08)!important;
  position:relative;z-index:10}

/* ── Hide Streamlit chrome ── */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"],
footer,#MainMenu,
[data-testid="stDecoration"]{display:none!important}
[data-testid="block-container"]{padding:0!important;max-width:100%!important}
[data-testid="column"]{padding:0!important}

/* ── Entrance animation ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.login-left{animation:fadeUp .5s cubic-bezier(.16,1,.3,1) both;padding-top:2rem}

/* ── Input fields ── */
[data-baseweb="input"]{
  background-color:rgba(248,249,250,0.9)!important;
  border-radius:10px!important;
  border:1.5px solid rgba(229,231,235,0.8)!important;
  transition:border-color .2s,box-shadow .2s!important;
  overflow:hidden!important}
[data-baseweb="input"]:focus-within{
  background-color:#fff!important;
  border-color:rgba(108,99,255,0.6)!important;
  box-shadow:0 0 0 3px rgba(108,99,255,0.1)!important}
[data-baseweb="input"]>div{background:transparent!important}
[data-baseweb="input"] input{
  background:transparent!important;color:#111827!important;
  font-size:15px!important;padding:13px 16px!important;
  border:none!important;outline:none!important;height:auto!important}
[data-baseweb="input"] input::placeholder{color:#9CA3AF!important}
[data-baseweb="input"] input:-webkit-autofill,
[data-baseweb="input"] input:-webkit-autofill:hover,
[data-baseweb="input"] input:-webkit-autofill:focus{
  -webkit-box-shadow:0 0 0 30px #F3F4F6 inset!important;
  -webkit-text-fill-color:#111827!important}
[data-baseweb="input"]:focus-within input:-webkit-autofill{
  -webkit-box-shadow:0 0 0 30px #fff inset!important}
[data-baseweb="input"] div[aria-label="Toggle password visibility"],
[data-baseweb="input"] div[aria-label="unmask"]{color:#374151!important}
[data-baseweb="input"] div[aria-label="Toggle password visibility"] svg,
[data-baseweb="input"] div[aria-label="unmask"] svg,
[data-baseweb="input"] div[aria-label="Toggle password visibility"] svg path,
[data-baseweb="input"] div[aria-label="unmask"] svg path{fill:#374151!important;color:#374151!important}
[data-testid="stTextInput"] label p{
  font-weight:500!important;font-size:13px!important;
  color:#374151!important;margin-bottom:5px!important}

/* ── Primary button ── */
div.stButton>button[kind="primary"],div.stButton>button:first-child{
  background:linear-gradient(135deg,#6C63FF 0%,#4F46E5 100%)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:600!important;font-size:15px!important;
  padding:13px 20px!important;letter-spacing:.1px!important;
  box-shadow:0 4px 14px rgba(108,99,255,0.3)!important;
  transition:all .2s!important;width:100%!important;
  position:relative!important;overflow:hidden!important}
div.stButton>button[kind="primary"] p,
div.stButton>button:first-child p{color:#fff!important}
div.stButton>button[kind="primary"]:hover,
div.stButton>button:first-child:hover{
  background:linear-gradient(135deg,#5B54E0 0%,#4338CA 100%)!important;
  transform:translateY(-1px)!important;
  box-shadow:0 6px 20px rgba(108,99,255,0.4)!important}

/* ── Secondary button ── */
div.stButton>button[kind="secondary"]{
  background:#fff!important;color:#374151!important;
  border:1.5px solid #D1D5DB!important;border-radius:10px!important;
  font-weight:500!important;font-size:14px!important;
  padding:12px 20px!important;box-shadow:none!important;
  transition:all .2s!important;width:100%!important}
div.stButton>button[kind="secondary"] p{color:#374151!important}
div.stButton>button[kind="secondary"]:hover{
  border-color:#6C63FF!important;color:#6C63FF!important;
  background:#F5F3FF!important}
div.stButton>button[kind="secondary"]:hover p{color:#6C63FF!important}

/* ── Logo animation ── */
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes floatBeat{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-3px) scale(1.04)}}
.ir-logo-anim{animation:gradShift 4s ease infinite,floatBeat 4s ease-in-out infinite!important;background-size:200% 200%!important}

/* ── Checkbox — forced light-theme styling (overrides config.toml base=dark) ── */
label[data-baseweb="checkbox"]{outline:none!important}
label[data-baseweb="checkbox"]:has(input:checked) svg{fill:#fff!important;display:block!important}
/* Force checkbox label text to dark color — visible on light signup background */
label[data-baseweb="checkbox"] span,
label[data-baseweb="checkbox"] p,
.stCheckbox label span,
.stCheckbox label p,
.stCheckbox label,
[data-testid="stCheckbox"] label span,
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] label{color:#374151!important;-webkit-text-fill-color:#374151!important}
/* Force checkbox box to white background with purple border (unchecked state) */
label[data-baseweb="checkbox"] > div:first-child,
[data-baseweb="checkbox"] > div:first-child{
  background-color:#ffffff!important;background:#ffffff!important;
  border:2px solid #6C63FF!important;border-radius:4px!important;
  width:18px!important;height:18px!important;min-width:18px!important;min-height:18px!important;
  flex-shrink:0!important}
/* Checked state — purple background */
label[data-baseweb="checkbox"]:has(input:checked) > div:first-child,
[data-baseweb="checkbox"]:has(input:checked) > div:first-child{
  background-color:#6C63FF!important;background:#6C63FF!important;
  border-color:#6C63FF!important}

/* ── Google button ── */
.g-btn{display:flex;align-items:center;justify-content:center;gap:10px;
  width:100%;background:#fff;border:1.5px solid #E5E7EB;border-radius:10px;
  padding:12px 20px;font-family:'Inter',sans-serif;font-size:15px;font-weight:500;
  color:#374151;text-decoration:none;cursor:pointer;transition:all .2s;margin:4px 0}
.g-btn:hover{background:#F9FAFB;border-color:#D1D5DB}

/* ── Right panel ── */
.right-panel{
  min-height:100vh;
  background:linear-gradient(160deg,#1e1b4b 0%,#312e81 30%,#4338ca 60%,#6366f1 100%);
  display:flex;flex-direction:column;justify-content:center;
  padding:3rem 3.5rem;position:relative;overflow:hidden}
.right-panel .dot-grid{
  position:absolute;inset:0;
  background-image:radial-gradient(rgba(255,255,255,0.07) 1px,transparent 1px);
  background-size:24px 24px;pointer-events:none}
.right-panel .glow{
  position:absolute;border-radius:50%;pointer-events:none;filter:blur(80px)}
.feat-card{
  background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
  border-radius:16px;padding:20px;backdrop-filter:blur(12px);
  -webkit-backdrop-filter:blur(12px);transition:transform .3s,background .3s}
.feat-card:hover{background:rgba(255,255,255,0.12);transform:translateY(-2px)}
</style>"""


# ── Small helper boxes ─────────────────────────────────────────────────────────
def _ok(m):
    return (
        f'<div style="background:#DCFCE7;color:#16A34A;border-left:4px solid '
        f'#16A34A;border-radius:8px;padding:12px 16px;margin:8px 0;'
        f'font-size:14px;line-height:1.5">{m}</div>'
    )

def _err(m):
    return (
        f'<div style="background:#FEE2E2;color:#DC2626;border-left:4px solid '
        f'#DC2626;border-radius:8px;padding:12px 16px;margin:8px 0;'
        f'font-size:14px;line-height:1.5">{m}</div>'
    )


# ── Google "G" SVG ─────────────────────────────────────────────────────────────
_GOOGLE_SVG = (
    '<svg width="18" height="18" viewBox="0 0 18 18">'
    '<path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844'
    'c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.56 2.684-3.874 '
    '2.684-6.615z"/>'
    '<path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258'
    'c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332'
    'C2.438 15.983 5.482 18 9 18z"/>'
    '<path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707s.102'
    '-1.167.282-1.707V4.961H.957C.347 6.175 0 7.55 0 9s.348 2.826.957 4.039'
    'l3.007-2.332z"/>'
    '<path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58'
    'C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.961L3.964 7.293'
    'C4.672 5.166 6.656 3.58 9 3.58z"/>'
    '</svg>'
)


# ── Right panel HTML ───────────────────────────────────────────────────────────
_RIGHT_PANEL = (
    '<div class="right-panel">'
    '<div class="dot-grid"></div>'
    '<div class="glow" style="width:300px;height:300px;background:rgba(99,102,241,0.3);top:-5%;right:-8%"></div>'
    '<div class="glow" style="width:250px;height:250px;background:rgba(139,92,246,0.2);bottom:10%;left:-6%"></div>'
    '<div style="position:relative;z-index:2">'
    # Badge
    '<div style="display:inline-flex;align-items:center;gap:6px;'
    'background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);'
    'border-radius:100px;padding:6px 14px;margin-bottom:2rem;'
    'font-size:12px;font-weight:600;color:rgba(255,255,255,0.9);letter-spacing:.5px">'
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
    '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
    'JOIN 50,000+ USERS</div>'
    # Heading
    '<h2 style="font-size:36px;font-weight:800;color:#fff;margin:0 0 12px;'
    'line-height:1.15;letter-spacing:-1px">'
    'Start your<br>'
    '<span style="background:linear-gradient(135deg,#a78bfa,#38bdf8);'
    '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
    'background-clip:text">personalized</span><br>journey today.</h2>'
    # Sub
    '<p style="font-size:15px;color:rgba(255,255,255,0.65);margin:0 0 2.5rem;'
    'max-width:340px;line-height:1.6">'
    'Create a free account and get instant access to AI-powered product '
    'recommendations tailored to your unique preferences.</p>'
    # Feature cards
    '<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:2.5rem">'
    # Card 1
    '<div class="feat-card"><div style="display:flex;align-items:center;gap:12px">'
    '<div style="width:36px;height:36px;border-radius:10px;'
    'background:rgba(167,139,246,0.2);display:flex;align-items:center;'
    'justify-content:center;flex-shrink:0">'
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2">'
    '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 '
    '3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>'
    '<path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 '
    '3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>'
    '</svg></div>'
    '<div><div style="font-size:14px;font-weight:600;color:#fff">Triple AI Engine</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px">'
    'Collaborative, Content-Based &amp; Sentiment engines</div></div></div></div>'
    # Card 2
    '<div class="feat-card"><div style="display:flex;align-items:center;gap:12px">'
    '<div style="width:36px;height:36px;border-radius:10px;'
    'background:rgba(56,189,248,0.2);display:flex;align-items:center;'
    'justify-content:center;flex-shrink:0">'
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2">'
    '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg></div>'
    '<div><div style="font-size:14px;font-weight:600;color:#fff">Cold-Start Solver</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px">'
    'Get great recommendations from your very first visit</div></div></div></div>'
    # Card 3
    '<div class="feat-card"><div style="display:flex;align-items:center;gap:12px">'
    '<div style="width:36px;height:36px;border-radius:10px;'
    'background:rgba(52,211,153,0.2);display:flex;align-items:center;'
    'justify-content:center;flex-shrink:0">'
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>'
    '<div><div style="font-size:14px;font-weight:600;color:#fff">Privacy First</div>'
    '<div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px">'
    'Your data is encrypted and never shared with third parties</div></div></div></div>'
    '</div>'
    # Trust bar
    '<div style="display:flex;align-items:center;gap:20px;padding-top:8px">'
    '<div style="display:flex;align-items:center;gap:6px;color:rgba(255,255,255,0.5);font-size:12px;font-weight:500">'
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>Encrypted</div>'
    '<div style="width:1px;height:12px;background:rgba(255,255,255,0.15)"></div>'
    '<div style="display:flex;align-items:center;gap:6px;color:rgba(255,255,255,0.5);font-size:12px;font-weight:500">'
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 '
    '7 14.14 2 9.27 8.91 8.26 12 2"/></svg>Free Forever</div>'
    '<div style="width:1px;height:12px;background:rgba(255,255,255,0.15)"></div>'
    '<div style="display:flex;align-items:center;gap:6px;color:rgba(255,255,255,0.5);font-size:12px;font-weight:500">'
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>Real-time</div>'
    '</div>'
    '</div></div>'
)


# ── Logo HTML ──────────────────────────────────────────────────────────────────
_LOGO = """
<div style="display:flex;align-items:center;gap:10px;margin-bottom:2.5rem;padding-left:clamp(1.5rem,6vw,5rem)">
  <div class="ir-logo-anim" style="width:36px;height:36px;border-radius:10px;
    background:linear-gradient(135deg,#6C63FF 0%,#06B6D4 100%);
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 4px 14px rgba(108,99,255,0.35);flex-shrink:0">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M3 7h14l-1.5 9.5a1.5 1.5 0 01-1.493 1.3H5.993A1.5 1.5 0 014.5 16.5L3 7z"
            stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
      <line x1="2" y1="7" x2="18" y2="7" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="7"  cy="3.5" r="1.2" fill="white"/>
      <circle cx="10" cy="2"   r="1.2" fill="white"/>
      <circle cx="13" cy="3.5" r="1.2" fill="white"/>
      <line x1="7" y1="3.5" x2="10" y2="2"   stroke="white" stroke-width="1" stroke-linecap="round"/>
      <line x1="10" y1="2"  x2="13" y2="3.5" stroke="white" stroke-width="1" stroke-linecap="round"/>
      <line x1="7"  y1="3.5" x2="13" y2="3.5" stroke="white" stroke-width="0.8" stroke-linecap="round"/>
    </svg>
  </div>
  <span style="font-size:22px;font-weight:700;color:#6C63FF;letter-spacing:-0.5px">IntelliRec</span>
</div>
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Page
# ═══════════════════════════════════════════════════════════════════════════════
def render_signup():
    init_session()

    st.markdown(_FONT_LINK, unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)

    import streamlit.components.v1 as _cv1
    _cv1.html("""
<script>
(function(){
  var doc = window.parent.document;
  var _t = null;

  function fixCB(){
    doc.querySelectorAll('label[data-baseweb="checkbox"]').forEach(function(lbl){
      var inp = lbl.querySelector('input[type="checkbox"]');
      var chk = inp ? inp.checked : false;
      var bg  = chk ? '#6C63FF' : '#ffffff';

      /* Find the visual box: the div that is the direct parent of the SVG */
      var visualBox = null;
      var svg = lbl.querySelector('svg');
      if(svg){
        var el = svg.parentElement;
        while(el && el !== lbl){
          if(el.tagName === 'DIV'){ visualBox = el; break; }
          el = el.parentElement;
        }
      }
      /* Fallback: smallest div by area (avoids text container) */
      if(!visualBox){
        var best = null, bestArea = Infinity;
        Array.from(lbl.querySelectorAll('div')).forEach(function(d){
          var r = d.getBoundingClientRect();
          var a = r.width * r.height;
          if(a > 50 && a < 800 && a < bestArea){ bestArea=a; best=d; }
        });
        visualBox = best;
      }

      /* Clear all div backgrounds so nothing else turns purple */
      lbl.style.setProperty('background','transparent','important');
      lbl.style.setProperty('background-color','transparent','important');
      Array.from(lbl.querySelectorAll('div')).forEach(function(d){
        if(d !== visualBox){
          d.style.setProperty('background','transparent','important');
          d.style.setProperty('background-color','transparent','important');
        }
      });

      if(!visualBox) return;
      visualBox.style.setProperty('background',      bg, 'important');
      visualBox.style.setProperty('background-color',bg, 'important');
      visualBox.style.setProperty('border',    '2px solid #6C63FF','important');
      visualBox.style.setProperty('border-radius',   '4px','important');
      visualBox.style.setProperty('min-width',  '18px','important');
      visualBox.style.setProperty('min-height', '18px','important');
      visualBox.style.setProperty('width',  '18px','important');
      visualBox.style.setProperty('height', '18px','important');
      visualBox.style.setProperty('flex-shrink','0','important');
      if(svg){
        svg.style.setProperty('fill','#ffffff','important');
        svg.style.setProperty('display', chk ? 'block':'none','important');
      }

      /* Force label text to dark color — visible on light signup background */
      lbl.querySelectorAll('span,p').forEach(function(txt){
        txt.style.setProperty('color','#374151','important');
        txt.style.setProperty('-webkit-text-fill-color','#374151','important');
      });
    });
  }

  fixCB();
  [50,100,200,400,700,1200,2000].forEach(function(ms){ setTimeout(fixCB,ms); });

  /* Watch only structural changes + aria-checked — avoids infinite loop
     caused by watching 'style' (our own setProperty would re-trigger it) */
  var obs = new MutationObserver(function(muts){
    var relevant = muts.some(function(m){
      return m.type==='childList' || m.attributeName==='aria-checked';
    });
    if(!relevant) return;
    clearTimeout(_t); _t = setTimeout(fixCB, 60);
  });
  obs.observe(doc.body,{childList:true,subtree:true,
    attributes:true,attributeFilter:['aria-checked']});
})();
</script>
""", height=0)

    left, right = st.columns([46, 54])

    # ── LEFT: Form ─────────────────────────────────────────────────────────────
    with left:
        st.markdown("<div class='login-left'>", unsafe_allow_html=True)
        st.markdown("<div style='height:4vh;min-height:28px'></div>", unsafe_allow_html=True)

        # Logo
        st.markdown(_LOGO, unsafe_allow_html=True)

        # Heading
        st.markdown(
            '<div style="padding:0 clamp(1.5rem,6vw,5rem);margin-bottom:1.8rem">'
            '<h1 style="font-size:28px;font-weight:700;color:#111827;margin:0 0 5px;'
            'letter-spacing:-.5px">Create your account</h1>'
            '<p style="font-size:15px;color:#6B7280;margin:0">'
            'Free forever &middot; No credit card required</p></div>',
            unsafe_allow_html=True,
        )

        _, form_col, _ = st.columns([0.12, 0.76, 0.12])
        with form_col:

            # Show success state if signup just completed
            if st.session_state.get("_su_success_email"):
                confirmed_email = st.session_state["_su_success_email"]
                st.markdown(
                    _ok(
                        f"<strong>Account created!</strong> We sent a verification "
                        f"email to <strong>{confirmed_email}</strong>.<br>"
                        f"Click the link in the email to activate your account, "
                        f"then come back here to sign in."
                    ),
                    unsafe_allow_html=True,
                )
                # Convert Supabase #access_token hash to ?confirmed=1 query param
                st.markdown("""
<script>
(function() {
  var h = window.location.hash;
  if (h && h.includes('type=signup')) {
    window.location.href = window.location.origin + window.location.pathname + '?confirmed=1';
  }
})();
</script>""", unsafe_allow_html=True)
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                if st.button("Back to Sign In", use_container_width=True,
                             type="primary", key="su_back_success"):
                    st.session_state.pop("_su_success_email", None)
                    st.session_state.show_signup = False
                    st.rerun()
            else:
                full_name = st.text_input("Full Name", placeholder="Your full name", key="su_name")
                email = st.text_input("Email address", placeholder="you@example.com", key="su_email")
                password = st.text_input(
                    "Password", type="password",
                    placeholder="Minimum 6 characters", key="su_pass",
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                terms = st.checkbox(
                    "I agree to the Terms of Service and Privacy Policy", key="su_terms"
                )
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                if st.button("Create Account", use_container_width=True,
                             type="primary", key="su_btn"):
                    if not all([full_name, email, password]):
                        st.markdown(_err("Please fill in all fields."), unsafe_allow_html=True)
                    elif len(password) < 6:
                        st.markdown(
                            _err("Password must be at least 6 characters."),
                            unsafe_allow_html=True,
                        )
                    elif not terms:
                        st.markdown(
                            _err("Please accept the Terms of Service."),
                            unsafe_allow_html=True,
                        )
                    else:
                        with st.spinner("Creating account..."):
                            success, msg = signup_user(email, password, full_name)
                        if success:
                            st.session_state["_su_success_email"] = email
                            st.rerun()
                        elif "already exists" in msg.lower() or "already registered" in msg.lower():
                            st.markdown(
                                _err("An account with this email already exists. Please sign in instead."),
                                unsafe_allow_html=True,
                            )
                            if st.button("→ Sign In", key="su_goto_signin",
                                         type="primary", use_container_width=True):
                                st.session_state.show_signup = False
                                st.rerun()
                        elif "rate limit" in msg.lower() or "email rate" in msg.lower():
                            st.markdown(
                                _err("Too many sign-up attempts. Please wait 10 minutes and try again, "
                                     "or contact support if this persists."),
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                _err(f"Sign-up failed: {msg}"), unsafe_allow_html=True
                            )

                # Divider
                st.markdown(
                    '<div style="display:flex;align-items:center;gap:12px;margin:16px 0">'
                    '<div style="flex:1;height:1px;background:#E5E7EB"></div>'
                    '<span style="font-size:12px;color:#9CA3AF;font-weight:500">or</span>'
                    '<div style="flex:1;height:1px;background:#E5E7EB"></div></div>',
                    unsafe_allow_html=True,
                )

                if st.button("Back to Sign In", use_container_width=True,
                             type="secondary", key="su_back"):
                    st.session_state.show_signup = False
                    st.rerun()

                # Google divider
                st.markdown(
                    '<div style="display:flex;align-items:center;gap:12px;margin:12px 0">'
                    '<div style="flex:1;height:1px;background:#E5E7EB"></div>'
                    '<span style="font-size:12px;color:#9CA3AF;font-weight:500">'
                    'or sign up with</span>'
                    '<div style="flex:1;height:1px;background:#E5E7EB"></div></div>',
                    unsafe_allow_html=True,
                )

                # Google button
                _g_url = login_with_google()
                _g_href = _g_url if _g_url else "#"
                st.markdown(
                    f'<a href="{_g_href}" target="_self" class="g-btn">'
                    f'{_GOOGLE_SVG} Sign up with Google</a>',
                    unsafe_allow_html=True,
                )
                if not _g_url:
                    st.markdown(
                        _err("Google sign-up unavailable - check Supabase config."),
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:4vh;min-height:28px'></div>", unsafe_allow_html=True)

    # ── RIGHT: Enterprise branded panel ────────────────────────────────────────
    with right:
        st.markdown(_RIGHT_PANEL, unsafe_allow_html=True)


show_signup_page = render_signup
