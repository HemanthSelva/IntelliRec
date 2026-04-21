import sys

def patch_signup():
    with open('d:/Desktop/IntelliRec/auth/login.py', 'r', encoding='utf-8') as f:
        login_lines = f.readlines()
        
    with open('d:/Desktop/IntelliRec/auth/signup.py', 'r', encoding='utf-8') as f:
        signup_lines = f.readlines()

    # In login.py, _CSS starts at line 8
    # _RIGHT ends around line 434 (where """ is)
    css_right_content = []
    start_capture = False
    for i, line in enumerate(login_lines):
        if i == 7: # 0-indexed line 8
            start_capture = True
        if start_capture:
            css_right_content.append(line)
        if i == 434: # 0-indexed line 435
            break
            
    # In signup.py, replace lines 8 to 376 (0-indexed 7 to 375)
    new_signup_lines = signup_lines[:7] + css_right_content + signup_lines[376:]
    
    # Write it back temporarily
    with open('d:/Desktop/IntelliRec/auth/signup.py', 'w', encoding='utf-8') as f:
        f.writelines(new_signup_lines)

    # Now let's handle the string replacements using read/write
    with open('d:/Desktop/IntelliRec/auth/signup.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace('def render_signup():\n    init_session()\n    st.markdown(_INTER', 
'''def render_signup():
    init_session()

    st.markdown("""
<div class="glass-mesh">
  <div style="position:absolute;top:-10%;left:-10%;width:400px;height:400px;background:rgba(108,99,255,0.08);border-radius:50%;filter:blur(80px);animation: fadeUp 15s infinite alternate ease-in-out;"></div>
  <div style="position:absolute;bottom:-10%;right:40%;width:300px;height:300px;background:rgba(6,182,212,0.08);border-radius:50%;filter:blur(60px);animation: fadeRight 12s infinite alternate ease-in-out;"></div>
  <div style="position:absolute;top:30%;right:45%;width:200px;height:200px;background:rgba(79,70,229,0.06);border-radius:50%;filter:blur(40px);animation: fadeUp 10s infinite alternate ease-in-out;"></div>
</div>
""", unsafe_allow_html=True)
    
    st.markdown(_INTER''')

    content = content.replace('"G  Sign up with Google"', '"Sign up with Google"')
    
    with open('d:/Desktop/IntelliRec/auth/signup.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print('Patched signup.py successfully.')
    
patch_signup()
