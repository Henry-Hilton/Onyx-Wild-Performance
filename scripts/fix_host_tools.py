#!/usr/bin/env python3
from pathlib import Path
path=Path('/root/onyx-kernel-dev/kernel/certs/extract-cert.c')
text=path.read_text()
# Android's BoringSSL support uses a different feature guard than mainline.
# Keep the PIN declaration and initialization under the same guard as the
# existing ENGINE branch when building against the Linux host's OpenSSL.
text=text.replace('#ifdef USE_PKCS11_ENGINE\nstatic const char *key_pass;',
                  '#ifndef OPENSSL_IS_BORINGSSL\nstatic const char *key_pass;')
text=text.replace('#ifdef USE_PKCS11_ENGINE\n\tkey_pass = getenv("KBUILD_SIGN_PIN");',
                  '#ifndef OPENSSL_IS_BORINGSSL\n\tkey_pass = getenv("KBUILD_SIGN_PIN");')
path.write_text(text)
