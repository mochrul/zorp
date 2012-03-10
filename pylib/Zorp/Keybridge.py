############################################################################
##
## Copyright (c) 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
## 2010, 2011 BalaBit IT Ltd, Budapest, Hungary
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##
############################################################################

"""
<module maturity="stable">
  <summary>The Keybridge module implements generic X.509 key bridging.</summary>
  <description>
    <para>Keybridging is a method to let the client see a copy of the server's certificate (or vice versa), allowing it to inspect it and decide about its trustworthiness. Because of proxying the SSL/TLS connection, the client is not able to inspect the certificate of the server directly, therefore Zorp generates a certificate based on the server's certificate on-the-fly. This generated certificate is presented to the client.</para>
    <para>For details on configuring keybridging, see <xref linkend="keybridging"/>.</para>
  </description>
</module>
"""

from Zorp import *

import os
import fcntl
import OpenSSL
import hashlib

#
# Key selector is a hash containing one or more ways to
# identify a key or keypair. The meaning of various keys in the hash and how they are interpreted
# is as follows:
#
# 'zms-key'              Contains the unique name of a keypair in ZMS
# 'bridge-trusted-key'   Contains a certificate blob for which a new key can be generated,
#                        the key must be signed by the 'trusted' CA
# 'bridge-untrusted-key' Contains a certificate blob for which a new key can be generated,
#                        the key must be signed by the 'untrusted' CA.
#

class X509KeyManager(object):
        """<class type="x509keymanager" internal="yes">
        </class>"""
        def __init__(self):
                pass

        def getKeypair(self, selector):
                pass

class X509KeyBridge(X509KeyManager):
        """<class type="x509keymanager">
        <summary>
          Class to perform SSL keybridging.
        </summary>
        <description>
          <para>
            This class is able to generate certificates mimicking another
            certificate, primarily used to transfer the information of a server's certificate to the client in keybridging. For details on configuring keybridging, see <xref linkend="keybridging"/>.
          </para>
        </description>
        <metainfo>
          <attributes>
              <attribute>
                  <name>key_file</name>
                  <type>
                      <string/>
                  </type>
                  <default>""</default>
                  <description>Name of the private key to be used for the newly generated certificates.</description>
              </attribute>
              <attribute>
                <name>key_passphrase</name>
                <type>
                    <string/>
                </type>
                <default>""</default>
                <description>Passphrase required to access the private key stored in <parameter>key_file</parameter>.</description>
              </attribute>
              <attribute>
                <name>cache_directory</name>
                <type>
                    <string/>
                </type>
                <default>""</default>
                <description>The directory where all automatically generated certificates are cached.</description>
              </attribute>
              <attribute>
                <name>trusted_ca_files</name>
                    <type>
                        <certificate cert="yes" key="yes" ca="yes"/>
                    </type>
                    <default>None</default>
                    <description>A tuple of <parameter>cert_file</parameter>, <parameter>key_file</parameter>, <parameter>passphrase</parameter>) for the CA used for keybridging trusted certificates.</description>
              </attribute>
              <attribute>
                    <name>untrusted_ca_files</name>
                    <type>
                      <certificate cert="yes" key="yes" ca="yes"/>
                    </type>
                    <default>None</default>
                    <description>A tuple of <parameter>cert_file</parameter>, <parameter>key_file</parameter>, <parameter>passphrase</parameter>) for the CA used for keybridging untrusted certificates.</description>
              </attribute>
          </attributes>
        </metainfo>
        </class>"""

        default_extension_whitelist = ('keyUsage', 'subjectAltName', 'extendedKeyUsage')

        def __init__(self, key_file, cache_directory=None, trusted_ca_files=None, untrusted_ca_files=None, key_passphrase = "",
                     extension_whitelist=None):
                """<method maturity="stable">
                  <metainfo>
                    <arguments>
                      <argument>
                        <name>key_file</name>
                        <type>
                          <certificate key="yes" cert="no"/>
                        </type>
                        <description>Name of the private key to be used for the newly generated certificates.</description>
                      </argument>
                      <argument>
                        <name>key_passphrase</name>
                        <type>
                          <string/>
                        </type>
                        <default>""</default>
                        <description>Passphrase required to access the private key stored in <parameter>key_file</parameter>.</description>
                      </argument>
                      <argument>
                        <name>cache_directory</name>
                        <type>
                          <string/>
                        </type>
                        <default>"/var/lib/zorp/keybridge-cache"</default>
                        <description>The directory where all automatically generated certificates are cached.</description>
                      </argument>
                      <argument>
                        <name>trusted_ca_files</name>
                        <type>
                          <certificate cert="yes" key="yes" ca="yes"/>
                        </type>
                        <description>A tuple of <parameter>cert_file</parameter>, <parameter>key_file</parameter>,
                          <parameter>passphrase</parameter>) for the CA used for keybridging trusted certificates.
                        </description>
                      </argument>
                      <argument>
                        <name>untrusted_ca_files</name>
                        <type>
                          <certificate cert="yes" key="yes" ca="yes"/>
                        </type>
                        <default>None</default>
                        <description>A tuple of <parameter>cert_file</parameter>, <parameter>key_file</parameter>,
                          <parameter>passphrase</parameter>) for the CA used for keybridging untrusted certificates.
                        </description>
                      </argument>
                      <argument>
                        <name>extension_whitelist</name>
                        <type>
                          <list><string/></list>
                        </type>
                        <default>None</default>
                        <description>
                            <para>Zorp transfers the following certificate extensions to the client side: <parameter>Key Usage</parameter>, <parameter>Subject Alternative Name</parameter>, <parameter>Extended Key Usage</parameter>. Other extensions will be automatically deleted during keybridging. This is needed because some certificate extensions contain references to the Issuer CA, which references become invalid for keybridged certificates. To transfer other extensions, list them in the <parameter>extension_whitelist</parameter> parameter. Note that modifying this parameter replaces the default values, so to extend the list of transferred extensions, include the <parameter>'keyUsage', 'subjectAltName', 'extendedKeyUsage'</parameter> list as well. For example:</para>
                            <synopsis>self.extension_whitelist = ('keyUsage', 'subjectAltName', 'extendedKeyUsage', 'customExtension')</synopsis>
                        </description>
                      </argument>
                    </arguments>
                  </metainfo>
                </method>"""

                """Constructor to initialize an X509KeyBridge instance

                This constructor initializes an X509KeyBridge instance by
                loading the necessary keys and certificates from files. Make
                sure that it is initialized once, instead of in every proxy
                instance as that may degrade performance. This may be
                achieved by putting the initialization into the class body
                or into global context.

                Arguments

                  key_file  -- name of the private key to be used for all newly generated certificates

                  key_passphrase  -- passphrase to use with private key key_file

                  cache_directory -- name of a directory where all automatically generated certificates are cached

                  trusted_ca_files -- a tuple of (cert_file, key_file, passphrase) for a CA to be used for signing certificates

                  untrusted_ca_files -- a tuple of (cert_file, key_file, passphrase) for a CA to be used for signing untrusted certificates

                """
                if cache_directory:
                        self.cache_directory = cache_directory
                else:
                        self.cache_directory = "/var/lib/zorp/keybridge-cache"
                if not trusted_ca_files:
                        trusted_ca_files = (None, None, None)
                if not extension_whitelist:
                        extension_whitelist = self.default_extension_whitelist
                self.extension_whitelist = extension_whitelist
                self.initialized = 0
                try:
                        self.key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(key_file, 'r').read(), key_passphrase)
                        try:
                                passphrase = trusted_ca_files[2]
                        except IndexError:
                                passphrase = ""
                        self.trusted_ca = (OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(trusted_ca_files[0], 'r').read()),
                                           OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(trusted_ca_files[1], 'r').read(), passphrase))
                        if untrusted_ca_files:
                                try:
                                        passphrase = untrusted_ca_files[2]
                                except IndexError:
                                        passphrase = ""
                                self.untrusted_ca = (OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(untrusted_ca_files[0], 'r').read()),
                                                     OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(untrusted_ca_files[1], 'r').read(), passphrase))
                        try:
                                self.lock_file = open('%s/.lock' % self.cache_directory, 'r+')
                        except IOError:
                                self.lock_file = open('%s/.lock' % self.cache_directory, 'w')
                        self.initialized = 1
                except IOError, e:
                        log(None, CORE_ERROR, 3, "Error opening lock, key or certificate file for keybridge; file='%s', error='%s'", (e.filename, e.strerror))

        def __del__(self):
                """<method internal="yes">
                </method>"""
                if hasattr(self, "lock_file"):
                        self.lock_file.close()

        def getCachedKey(self, cert_file, cert_server):
                """<method internal="yes">
                </method>"""
                try:
                        log(None, CORE_DEBUG, 5, "Loading cached certificate; file='%s'", cert_file)
                        try:
                                orig_cert = open(cert_file + '.orig', 'r').read()
                        except IOError:
                                orig_cert = ''
                                log(None, CORE_DEBUG, 5, "Original keybridged certificate not found, regenerating; file='%s'", cert_file)
                        if orig_cert == cert_server:
                                cert = open(cert_file, 'r').read()
                                log(None, CORE_DEBUG, 5, "Cached certificate ok, reusing; file='%s'", cert_file)
                                return (cert, OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, self.key))
                        else:
                                log(None, CORE_DEBUG, 5, "Cached certificate changed, regenerating; file='%s'", cert_file)
                                try:
                                        os.unlink(cert_file)
                                except OSError:
                                        pass
                                try:
                                        os.unlink(cert_file + '.orig')
                                except OSError:
                                        pass
                                raise KeyError, 'certificate changed'
                except IOError, e:
                        # not in the cache
                        log(None, CORE_DEBUG, 5, "I/O error loading cached certificate, regenerating; file='%s', error='%s'", (cert_file, e.strerror))
                        raise KeyError, 'not in the cache'

        def storeCachedKey(self, cert_file, new_blob, orig_blob):
                """<method internal="yes">
                </method>"""
                try:
                        log(None, CORE_DEBUG, 5, "Storing cached certificate; file='%s'", cert_file)
                        f = open(cert_file, 'w')
                        f.write(new_blob)
                        f.close()
                        f = open(cert_file + '.orig', 'w')
                        f.write(orig_blob)
                        f.close()
                except IOError, e:
                        log(None, CORE_ERROR, 2, "Error storing generated X.509 certificate in the cache; file='%s', error='%s'", (cert_file, e.strerror))

        def lock(self):
                """<method internal="yes">
                </method>"""
                fcntl.lockf(self.lock_file, fcntl.LOCK_EX)

        def unlock(self):
                """<method internal="yes">
                </method>"""
                fcntl.lockf(self.lock_file, fcntl.LOCK_UN)

        def getLastSerial(self):
                """<method internal="yes">
                </method>"""
                serial = 1
                for file in os.listdir(self.cache_directory):
                        if file[-4:] != '.crt':
                                continue

                        f = open("%s/%s" % (self.cache_directory, file), 'r')
                        data = f.read()
                        f.close()

                        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, data)
                        cser = cert.get_serial_number()

                        if cser > serial:
                                serial = cser
                return serial

        def genCert(self, key, orig_cert, ca_cert, ca_key, serial):
                        """<method internal="yes">
                        </method>"""
                        filetype = OpenSSL.crypto.FILETYPE_PEM

                        new_cert = OpenSSL.crypto.load_certificate(filetype, OpenSSL.crypto.dump_certificate(filetype, orig_cert))
                        new_cert.set_serial_number(serial)
                        new_cert.set_issuer(ca_cert.get_subject())
                        new_cert.set_pubkey(key)
                        if ca_key.type() == OpenSSL.crypto.TYPE_DSA:
                                hash_alg = "DSA-SHA1"      # taken from openssl-0.9.8i/crypto/objects/obj_dat.h
                        else:
                                hash_alg = "md5"

                        # delete extensions not on whitelist
                        ext_index = 0
                        while ext_index < new_cert.get_extension_count():
                                ext = new_cert.get_extension(ext_index)
                                if ext.get_short_name() not in self.extension_whitelist:
                                        new_cert.del_extension(ext_index)
                                else:
                                        ext_index += 1

                        new_cert.sign(ca_key, hash_alg)

                        return new_cert

        def getKeypair(self, selector):
                """<method internal="yes">
                </method>"""
                if not self.initialized:
                        log(None, CORE_ERROR, 3, "Keybridge not completely initialized, error generating keypair;")
                        return (None, None)

                try:
                        trusted = 1
                        orig_blob = selector['bridge-trusted-key']
                except KeyError:
                        trusted = 0
                        orig_blob = selector['bridge-untrusted-key']

                hash = hashlib.md5(orig_blob).hexdigest()
                if trusted:
                        cert_file = '%s/trusted-%s.crt' % (self.cache_directory, hash)
                        ca_pair = self.trusted_ca
                else:
                        cert_file = '%s/untrusted-%s.crt' % (self.cache_directory, hash)
                        ca_pair = self.untrusted_ca

                self.lock()
                try:
                        try:
                                return self.getCachedKey(cert_file, orig_blob)
                        except KeyError:
                                log(None, CORE_DEBUG, 5, "Certificate not found in the cache, regenerating;")

                        serial_file = '%s/serial.txt' % self.cache_directory

                        serial_pos = ""
                        try:
                                serial_pos = "file open"
                                serial_file_fd = open(serial_file, 'r')
                                serial_pos = "file read"
                                serial_file_data = serial_file_fd.read().strip()
                                serial_pos = "turn to integer"
                                serial = int(serial_file_data)
                                serial_pos = None
                        except (ValueError, IOError):
                                serial = self.getLastSerial()
                                log(None, CORE_ERROR, 3, "On-line CA serial file not found, reinitializing; file='%s', serial='%d', pos='%s'", (serial_file, serial, serial_pos))

                        serial = serial + 1
                        try:
                                open(serial_file, 'w').write(str(serial))
                        except IOError, e:
                                log(None, CORE_ERROR, 2, "Cannot write serial number of on-line CA; file='%s', error='%s'", (serial_file, e.strerror))

                        orig_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, orig_blob)

                        new_cert = self.genCert(self.key, orig_cert, ca_pair[0], ca_pair[1], serial)

                        new_blob = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, new_cert)

                        self.storeCachedKey(cert_file, new_blob, orig_blob)

                        return (new_blob, OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, self.key))
                finally:
                        self.unlock()
