import random

def gen_captcha() -> dict:
    ops = [('+', lambda a, b: a + b), ('-', lambda a, b: a - b), ('x', lambda a, b: a * b)]
    a = random.randint(2, 12)
    b = random.randint(1, 9)
    op_sym, op_fn = random.choice(ops)
    if op_sym == '-' and b > a:
        a, b = b, a
    if op_sym == 'x':
        a, b = random.randint(2, 6), random.randint(2, 6)
    return {"a": a, "b": b, "op": op_sym, "answer": op_fn(a, b)}

def login(st, verificar_usuario, listar_usuarios_count):
    if not st.session_state.logged_in:
        _, col_c, _ = st.columns([1, 1.1, 1])
        with col_c:
            cap = st.session_state.captcha
            st.markdown(f"""
            <div style="margin-top:6vh" class="login-card">
                <div style="text-align:center;margin-bottom:1.75rem">
                    {LOGO_SVG}
                    <h1 style="font-size:1.9rem;font-weight:800;color:#0f172a;
                            letter-spacing:-0.03em;margin:0.4rem 0 0.15rem 0">Facturase</h1>
                    <p style="color:#64748b;font-size:0.82rem;margin:0">
                        Sistema de auditoria inteligente de facturas</p>
                </div>
                <hr style="border:none;border-top:1px solid #f1f5f9;margin:0 0 1.4rem 0">
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#374151;margin-bottom:0.2rem">Usuario</p>', unsafe_allow_html=True)
                username_in = st.text_input("Usuario", placeholder="Tu nombre de usuario", label_visibility="collapsed")
                st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#374151;margin:0.75rem 0 0.2rem 0">Contrasena</p>', unsafe_allow_html=True)
                password_in = st.text_input("Contrasena", type="password", placeholder="Tu contrasena", label_visibility="collapsed")
                st.markdown(f"""
                <div style="margin:0.9rem 0 0.3rem 0">
                    <p style="font-size:0.8rem;font-weight:600;color:#374151;margin-bottom:0.4rem">
                        Verificacion de seguridad</p>
                    <div style="background:#f1f5f9;border:2px dashed #cbd5e1;border-radius:10px;
                                padding:0.7rem;text-align:center;font-size:1.25rem;font-weight:700;
                                color:#0f172a;letter-spacing:0.2em;font-family:monospace">
                        {cap['a']} &nbsp; {cap['op']} &nbsp; {cap['b']} &nbsp; = &nbsp; ?
                    </div>
                </div>
                """, unsafe_allow_html=True)
                captcha_in = st.text_input("Resultado del captcha", placeholder="Escribe el resultado", label_visibility="collapsed")
                submitted = st.form_submit_button("Ingresar al sistema", type="primary", use_container_width=True)

                if submitted:
                    try:
                        captcha_ok = int(captcha_in.strip()) == st.session_state.captcha["answer"]
                    except ValueError:
                        captcha_ok = False

                    if not captcha_ok:
                        st.error("Verificacion incorrecta. Intenta de nuevo.")
                        st.session_state.captcha = generar_captcha()
                        st.rerun()
                    elif not username_in.strip() or not password_in:
                        st.error("Completa todos los campos.")
                    elif verificar_usuario(username_in.strip(), password_in):
                        st.session_state.logged_in = True
                        st.session_state.username = username_in.strip()
                        st.session_state.captcha = generar_captcha()
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                        st.session_state.captcha = generar_captcha()
                        st.rerun()

            if listar_usuarios_count() == 0:
                st.markdown("""
                <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;
                            padding:0.75rem 1rem;margin-top:0.75rem;font-size:0.82rem;color:#9a3412">
                    <strong>Sin usuarios configurados.</strong><br>
                    Ejecuta en consola del servidor:<br>
                    <code style="background:#fef3c7;padding:2px 6px;border-radius:4px">
                        python -m scripts.add_user
                    </code>
                </div>
                """, unsafe_allow_html=True)
        st.stop()
