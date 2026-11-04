"""Verify the signer of every JAR payload entry with the existing JDK."""

from pathlib import Path
import re
import tempfile

from .core import ReleaseError


# Keep the Java source in a Python module so it is covered by the frozen
# coordinator runtime's existing source hashes and needs no extra toolchain.
_VERIFIER = r'''
import java.io.OutputStream;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Locale;
import java.util.jar.JarFile;

class VerifyJarSigner {
    public static void main(String[] args) throws Exception {
        var names = new HashSet<String>();
        var sha256 = MessageDigest.getInstance("SHA-256");
        int verified = 0;
        try (var jar = new JarFile(args[0], true)) {
            var entries = jar.entries();
            while (entries.hasMoreElements()) {
                var entry = entries.nextElement();
                var name = entry.getName();
                var path = entry.isDirectory() ? name.substring(0, name.length() - 1) : name;
                if (!names.add(path) || path.contains("\\")) {
                    throw new SecurityException("Duplicate or ambiguous JAR entry: " + name);
                }
                for (var part : path.split("/", -1)) {
                    if (part.isEmpty() || part.equals(".") || part.equals("..")) {
                        throw new SecurityException("Ambiguous JAR entry: " + name);
                    }
                }
                if (entry.isDirectory()) {
                    if (entry.getSize() != 0) throw new SecurityException("Nonempty JAR directory: " + name);
                    continue;
                }
                var upper = name.toUpperCase(Locale.ROOT);
                if (upper.equals("META-INF/MANIFEST.MF") ||
                    upper.matches("META-INF/[^/]+\\.(SF|RSA|DSA|EC)")) continue;
                // Reading to EOF performs the JDK's signature and digest verification.
                try (var input = jar.getInputStream(entry)) {
                    input.transferTo(OutputStream.nullOutputStream());
                }
                var signers = entry.getCodeSigners();
                if (signers == null) throw new SecurityException("Unsigned JAR entry: " + name);
                if (signers.length != 1) throw new SecurityException("Multiple JAR signers: " + name);
                var leaf = signers[0].getSignerCertPath().getCertificates().get(0);
                var pin = HexFormat.of().formatHex(sha256.digest(leaf.getEncoded()));
                if (!pin.equals(args[1])) throw new SecurityException("JAR signer pin mismatch: " + name);
                verified++;
            }
        }
        if (verified == 0) throw new SecurityException("No signed JAR payload");
        System.out.println("Pinned signer verified for " + verified + " JAR payload entries");
    }
}
'''


def verify_jar_signer(ctx, path, pin):
    if not isinstance(pin, str) or not re.fullmatch(r'[0-9a-f]{64}', pin):
        raise ReleaseError('Missing or invalid SHA-256 signer pin')
    # Verify integrity and the pinned leaf, without using the OS CA store.
    # The owner's self-signed release certificate is an expected signer.
    with tempfile.TemporaryDirectory(prefix='release-jar-verify-') as folder:
        source = Path(folder) / 'VerifyJarSigner.java'
        source.write_text(_VERIFIER, encoding='ascii')
        ctx.command(['java', '--source', '17', source, Path(path).resolve(), pin])
