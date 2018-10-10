############################################################################
##
## Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2015-2018 BalaSys IT Ltd, Budapest, Hungary
##
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
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##
############################################################################

"""
<module maturity="stable">
  <summary>The Proxy module defines the abstract proxy class.</summary>
  <description>
    <para>
      This module encapsulates the ZorpProxy component
      implemented by the Zorp core. The Proxy module provides a common framework for
      protocol-specific proxies, implementing the functions that are used by all proxies.
      Protocol-specific proxy modules are derived from the Proxy module, and are
      described in <xref linkend="chapter_Proxies"/>.
    </para>
  </description>
  <metainfo>
  </metainfo>
</module>
"""

from Zorp import *
from Base import *
from Stream import Stream
from SockAddr import SockAddrInet
from Session import StackedSession, MasterSession
from Stack import getStackingProviderBackend
from Keybridge import *
from Chainer import ConnectChainer
from Exceptions import *
from Detector import *
from Encryption import *

import string, os, sys, traceback, re, types, inspect

def proxyLog(self, type, level, msg, args=None):
    """
    <function maturity="stable">
      <summary>
        Function to send a proxy-specific message to the system log.
      </summary>
      <description>
        <para>
          This function sends a message into the system log. All messages start with the
          <parameter>session_id</parameter> that uniquely identifies the connection.
        </para>
      </description>
      <metainfo>
        <arguments>
          <argument maturity="stable">
            <name>type</name>
            <type>
              <string/>
            </type>
            <description>
              The class of the log message.
            </description>
          </argument>
          <argument maturity="stable">
            <name>level</name>
            <type>
              <integer/>
            </type>
            <description>
              Verbosity level of the log message.
            </description>
          </argument>
          <argument maturity="stable">
            <name>msg</name>
            <type>
              <string/>
            </type>
            <description>
              The text of the log message.
            </description>
          </argument>
        </arguments>
      </metainfo>
    </function>
    """
    ## NOLOG ##
    log(self.session.session_id, type, level, msg, args)

class Proxy(BuiltinProxy):
    """
    <class maturity="stable" abstract="yes">
      <summary>
        Class encapsulating the abstract Zorp proxy.
      </summary>
      <description>
        <para>
          This class serves as the abstact base class for all proxies implemented
          in Zorp. When an instance of the Proxy class is created, it loads and starts a protocol-specific proxy.
          Proxies operate in their own threads, so this constructor returns immediately.
        </para>
      </description>
      <metainfo>
        <attributes>
          <attribute maturity="stable" internal="yes">
            <name>session</name>
            <type>Session instance</type>
            <description>The session inspected by the proxy.</description>
          </attribute>
          <attribute maturity="stable" internal="yes">
            <name>name</name>
            <type>
              <string/>
            </type>
            <description>The protocol-specific proxy class inspecting the traffic.</description>
          </attribute>
          <attribute maturity="stable" global="yes" internal="yes">
            <name>auth_inband_defer</name>
            <type>
              <boolean/>
            </type>
            <default>FALSE</default>
            <conftime>
              <read/>
              <write/>
            </conftime>
            <runtime>
              <read/>
            </runtime>
            <description>
            Set this parameter to <parameter>TRUE</parameter> to enable the protocol-specific proxy to perform
            inband authentication. This has effect only if the <link linkend="python.Auth">AuthenticationPolicy</link> used in
            the service requests InbandAuthentication.
            </description>
          </attribute>
          <attribute>
            <name>language</name>
            <type>
              <string/>
            </type>
            <default>en</default>
            <conftime>
              <read/>
              <write/>
            </conftime>
            <runtime>
              <read/>
            </runtime>
            <description>
              Determines the language used for user-visible error messages.
              Supported languages: <parameter>en</parameter> - English;
              <parameter>de</parameter> - German; <parameter>hu</parameter> - Hungarian.
            </description>
          </attribute>
          <attribute state="stable">
            <name>encryption_policy</name>
            <type>
              <class filter="encryptionpolicy" instance="no" existing="yes"/>
            </type>
            <default>None</default>
            <conftime>
              <read/>
              <write/>
            </conftime>
            <runtime/>
            <description>Name of the Encryption policy instance used to
            encrypt the sessions and verify the certificates used.
            For details, see <xref linkend="python.Encryption"/>.
            </description>
          </attribute>
        </attributes>
      </metainfo>
    </class>
    """
    name = None
    module = None
    auth_inband_defer = FALSE
    auth_inband_supported = FALSE
    auth_server_supported = FALSE

    def __init__(self, session):
        """
        <method internal="yes">
          <summary>
            Constructor to initialize an instance of the Proxy class.
          </summary>
          <description>
            <para>
              This constructor creates a new Proxy instance
              which creates an instance of the protocol-specific proxy class.
            </para>
          </description>
          <metainfo>
            <arguments>
              <argument maturity="stable">
                <name>name</name>
                <type></type>
                <description>The protocol-specific proxy class inspecting the traffic.</description>
              </argument>
              <argument maturity="stable">
                <name>session</name>
                <type>SESSION</type>
                <description>The session inspected by the proxy.</description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """
        # NOTE: circular reference, it is resolved in the __destroy__ method
        self.session = session
        session.setProxy(self)
        self.server_fd_picked = FALSE
        self.proxy_started = FALSE

        ## LOG ##
        # This message reports that a new proxy instance was started.
        ##
        log(session.session_id, CORE_SESSION, 5, "Proxy starting; class='%s', proxy='%s'", (self.__class__.__name__, self.name))
        if session.owner:
            parent = session.owner.proxy
        else:
            parent = None
        if not self.module:
            self.module = self.name

        super(Proxy, self).__init__(self.name, self.module, session.session_id, session.client_stream, parent)

    def __del__(self):
        """
        <method internal="yes">
          <summary>
            Destructor to deinitialize a Proxy instance.
          </summary>
          <description>
            <para>
              This destructor is called when this object instance is
              freed. It simply sends a message about this event to the
              log.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """

        ## LOG ##
        # This message reports that this proxy instance was ended.
        ##
        log(self.session.session_id, CORE_SESSION, 5, "Proxy ending; class='%s', module='%s'", (self.__class__.__name__, self.name))

    def __pre_startup__(self):
        """
        <method internal="yes">
        </method>
        """
        pass

    def __pre_config__(self):
        """
        <method internal="yes">
          <summary>
            Function called by the proxy core to perform internal proxy initialization.
          </summary>
          <description>
            <para>
              This function is similar to config() to perform initialization
              of internal proxy related data. It is not meant as a user
              interface, currently it is used to perform outband authentication.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        if not self.session.auth_user and self.session.service.authentication_policy:
            self.session.service.authentication_policy.performAuthentication(self.session)

        # hack: decrease timeout for UDP sessions
        if (self.session.protocol == ZD_PROTO_UDP) and self.timeout > 60000:
            self.timeout = 60000
        self.language = config.options.language
        self.encryption_policy = None

    def __post_config__(self):
        """<method internal="yes">
        </method>
        """
        self.encryption = None
        if self.session.service.encryption_policy:
            self.encryption = self.session.service.encryption_policy.getEncryption()
        elif self.encryption_policy:
            self.encryption = getEncryptionPolicy(self.encryption_policy).getEncryption()
        else:
            self.encryption = Globals.none_encryption


    def config(self):
        """
        <method maturity="stable">
          <summary>
            Function called by the proxy core to initialize the proxy instance.
          </summary>
          <description>
            <para>
              This function is called during proxy startup. It sets the attributes of the proxy instance according
               to the configuration of the proxy.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        pass

    def closedByAbort(self):
        """
        <method maturity="stable">
          <summary>
            Function called by the proxy core when an abort has been occured.
          </summary>
          <description>
            <para>
              This function is called when a callback gives abort or no result. It simply sets a flag that
              will be used for logging the reason of the proxy's ending.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        mastersession = self.session.getMasterSession()
        if mastersession.verdict == ConnectionVerdict(ConnectionVerdict.ACCEPTED):
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.ABORTED_BY_POLICY_ACTION)

    def invalidPolicyCall(self):
        """
        <method maturity="stable">
          <summary>
            Invalid policy function called.
          </summary>
          <description>
            <para>
              This function is called when invalid policy function has been called.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        mastersession = self.session.getMasterSession()
        if mastersession.verdict == ConnectionVerdict(ConnectionVerdict.ACCEPTED):
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.INVALID_POLICY_CALL)

    def __destroy__(self):
        """
        <method internal="yes">
          <summary>
            Function called by the proxy core when the session is to be freed.
          </summary>
          <description>
            <para>
              This function is called when the proxy module is to be freed. It
              simply sends a message about this event to the log.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        # NOTE: if C proxy was started but the chaining process was
        # not completed then the server side of the connection is
        # still hanging there unpicked. Close it.

        if self.proxy_started and self.session.server_stream and not self.server_fd_picked:
            self.session.server_stream.close()

        # free circular reference between session & proxy
        session = self.session
        del self.session.proxy
        delattr(self.session, self.name)

        ## LOG ##
        # This message reports that this proxy instance was destroyed and freed.
        ##
        log(self.session.session_id, CORE_DEBUG, 6, "Proxy destroy; class='%s', module='%s'", (self.__class__.__name__, self.name))
        # free possible circular references in __dict__ by removing all elements
        self.__dict__.clear()
        self.session = session

    def _stackProxyInSession(self, proxy_class, session):
        """
        <method internal="yes"/>
        """
        try:
            proxy = proxy_class(session)
            if ProxyGroup(1).start(proxy):
                return proxy
            else:
                raise RuntimeError, "Error starting proxy in group"

        except:
            ## LOG ##
            # This message indicates that an error occurred during child proxy stacking.
            # The stacking failed and the subsession is destroyed.
            ##
            proxyLog(self, CORE_ERROR, 2, "Error while stacking child proxy; error='%s', error_desc='%s', " % (sys.exc_info()[0], sys.exc_info()[1]))
            raise

    def stackProxyInSession(self, proxy_class, subsession, stack_info):
        """
        <method internal="yes"/>
        """
        subsession.stack_info = stack_info

        try:
            return self._stackProxyInSession(proxy_class, subsession)
        except:
            subsession.destroy()
            raise

    def stackProxy(self, client_stream, server_stream, proxy_class, stack_info):
        """
        <method internal="yes">
          <summary>
            Function to embed (stack) a proxy into the current proxy instance.
          </summary>
          <description>
            <para>
              This function stacks a new proxy into the current proxy instance. The function receives the
              downstream filedescriptors and the protocol-specific proxy class to embed.
              The way the underlying proxy decides which proxy_class
              to use is proxy specific.
            </para>
          </description>
          <metainfo>
            <arguments>
              <argument maturity="stable">
                <name>client_stream</name>
                <type></type>
                <description>The client-side data stream.</description>
              </argument>
              <argument maturity="stable">
                <name>server_stream</name>
                <type></type>
                <description>The server-side data stream.</description>
              </argument>
              <argument maturity="stable">
                <name>proxy_class</name>
                <type></type>
                <description>The protocol-specific proxy class to embed into the current proxy instance.
                </description>
              </argument>
              <argument maturity="stable">
                <name>stack_info</name>
                <type></type>
                <description>Meta-information provided by the parent proxy.
                </description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """

        proxyLog(self, CORE_DEBUG, 7, "Stacking child proxy; client_fd='%d', server_fd='%d', class='%s'", (client_stream.fd, server_stream.fd, proxy_class.__name__))

        # generate session ID for streams by replacing proxy name in the current value
        session_id_parts = string.split(self.session.session_id, '/')
        session_id_parts[-1] = proxy_class.name
        session_id = string.join(session_id_parts, '/')

        subsession = StackedSession(self.session)
        subsession.stack_info = stack_info
        subsession.client_stream = client_stream
        subsession.client_stream.name = "%s/client_upstream" % (session_id)
        subsession.server_stream = server_stream
        subsession.server_stream.name = "%s/server_upstream" % (session_id)

        try:
            return self._stackProxyInSession(proxy_class, subsession)
        except:
            subsession.destroy()
            raise

    def stackCustom(self, args):
        """
        <method maturity="stable" internal="yes">
          <summary>
            Function to perform custom stacking.
          </summary>
          <description>
            <para>
              This function is called by the underlying C proxy to
              stack a Stackin Provider (<parameter>Z_STACK_PROVIDER</parameter>), or to perform a customized
               stacking (<parameter>Z_STACK_CUSTOM</parameter>) stacking.
            </para>
          </description>
          <metainfo>
            <arguments>
              <argument maturity="stable">
                <name>args</name>
                <type></type>
                <description>A tuple of custom stacking arguments.</description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """

        ## LOG ##
        # This message reports that Zorp is about to stack a new proxy under the current proxy, as a child proxy.
        ##
        proxyLog(self, CORE_DEBUG, 7, "Stacking custom child; args='%s'", (str(args)))
        stack_info = None
        if isinstance(args[0], str):
            # this is a Z_STACK_PROVIDER stacking,
            # args[0] is provider name,
            # args[1] is stack_info argument
            stack_backend = getStackingProviderBackend(args[0])
            stack_info = args[1]
        else:
            # this is a Z_STACK_CUSTOM stacking
            # args[0] is an AbstractStackingBackend instance
            # args[1] is optional stack_info
            stack_backend = args[0]
            stack_info = args[1]
        return stack_backend.stack(stack_info)

    def setServerAddress(self, host, port):
        """
        <method maturity="stable">
          <summary>
            Function called by the proxy instance to set the
            address of the destination server.
          </summary>
          <description>
            <para>
              The proxy instance calls this function to set the
              address of the destination server.
              This function attempts to resolve the hostname of the server using the DNS;
              the result is stored in the <parameter>session.server_address</parameter> parameter.
              The address of the server may be modified later by the router of the service. See
              <xref linkend="python.Router"/> for details.
            </para>
            <note>
            <para>
            The <parameter>setServerAddress</parameter> function has effect
             only when <link linkend="python.Router.InbandRouter">InbandRouter</link>
              is used.
            </para>
            </note>
          </description>
          <metainfo>
            <arguments>
              <argument>
                <name>host</name>
                <type><string/></type>
                <description>The host name of the server.</description>
              </argument>
              <argument>
                <name>port</name>
                <type><integer/></type>
                <description>The Port number of the server.</description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """
        return self.session.setTargetAddressByHostname(host, port)

    def _connectServerInternal(self):
        """<method internal="yes"/>"""
        server_stream = None

        mastersession = self.session.getMasterSession()
        try:
            server_stream = self.session.chainer.chainParent(self.session)
        except ZoneException, s:
            ## LOG ##
            # This message indicates that no appropriate zone was found for the server address.
            # @see: Zone
            ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_POLICY)
            proxyLog(self, CORE_POLICY, 1, "Zone not found; info='%s'", (s,))
        except DACException, s:
            ## LOG ##
            # This message indicates that an DAC policy violation occurred.
            # It is likely that the new connection was not permitted as an inbound_service in the given zone.
            # @see: Zone
            ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_POLICY)
            proxyLog(self, CORE_POLICY, 1, "DAC policy violation; info='%s'", (s,))
            self.notifyEvent("core.dac_exception", [])
        except MACException, s:
            ## LOG ##
            # This message indicates that a MAC policy violation occurred.
            ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_POLICY)
            proxyLog(self, CORE_POLICY, 1, "MAC policy violation; info='%s'", (s,))
        except AAException, s:
            ## NOLOG ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_POLICY)
            proxyLog(self.self, CORE_POLICY, 1, "Authentication failure; info='%s'", (s,))
        except LimitException, s:
            ## NOLOG ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_LIMIT)
            proxyLog(self, CORE_POLICY, 1, "Connection over permitted limits; info='%s'", (s,))
        except LicenseException, s:
            ## NOLOG ##
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_LIMIT)
            proxyLog(self, CORE_POLICY, 1, "Attempt to use an unlicensed component, or number of licensed hosts exceeded; info='%s'", (s,))
        except:
            mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_UNKNOWN_FAIL)
            traceback.print_exc()
        else:
            is_silent_io_error = server_stream is None
            if is_silent_io_error:
                mastersession.verdict = ConnectionVerdict(ConnectionVerdict.DENIED_BY_CONNECTION_FAIL)

        return server_stream

    def connectServer(self):
        """
        <method maturity="stable">
          <summary>
            Function called by the proxy instance to establish the
            server-side connection.
          </summary>
          <description>
            <para>
              This function is called to establish the server-side connection.
              The function either connects a proxy to the destination server,
              or an embedded proxy to its parent proxy. The proxy may set the
               address of the destination server using the <function>setServerAddress</function>
                function.
            </para>
            <para>
              The <function>connectServer</function> function calls the chainer
              specified in the service definition to connect to the remote server
              using the host name and port parameters.
            </para>
            <para>
              The <function>connectServer</function> function returns the descriptor
               of the server-side data stream.
            </para>
          </description>
          <metainfo>
            <arguments/>
          </metainfo>
        </method>
        """
        if self.session.chainer == None:

            # we have no chainer, the server side fd
            # should be available by now, used in stacked
            # proxies
            if self.session.server_stream == None:
                raise InternalException, "No chainer and server_stream is None"

            if self.server_fd_picked:
                ## LOG ##
                # This message indicates an internal
                # error condition, more precisely a
                # non-toplevel proxy tried to
                # connect to the server side
                # multiple times, which is not
                # supported. Please report this
                # event to the BalaSys Development
                # Team (at devel@balasys.hu).
                ##
                log(self.session.session_id, CORE_ERROR, 1, "Internal error, stacked proxy reconnected to server multiple times;")
                return None
            self.server_fd_picked = TRUE

        else:
            self.server_fd_picked = TRUE
            self.session.server_stream = self._connectServerInternal()

        return self.session.server_stream

    def userAuthenticated(self, entity,
                          auth_info=''
                          ):
        """
        <method maturity="stable">
          <summary>
            Function called when inband authentication is successful.
          </summary>
          <description>
            <para>
              The proxy instance calls this function to
              indicate that the inband authentication was successfully
              performed. The name of the client is stored in the
              <parameter>entity</parameter> parameter.
            </para>
          </description>
          <metainfo>
          <arguments>
              <argument maturity="stable">
                <name>entity</name>
                <type></type>
                <description>Username of the authenticated client.</description>
              </argument>
            </arguments>
          </metainfo>
        </method>
        """
        self.session.getMasterSession().auth_user = entity
        self.session.auth_info = auth_info
        ## LOG ##
        # This message reports that the user authentication was successful.
        ##
        proxyLog(self, CORE_AUTH, 3, "User authentication successful; entity='%s', auth_info='%s'", (entity, auth_info))
        update_szig = {'auth_user': entity,
                       'auth_info': auth_info,
                       'auth_groups': str(groups),}

        if auth_info == 'gw-auth':
            update_szig["gateway_user"] = entity
            update_szig["gateway_groups"] = str(groups)
        elif auth_info == 'server':
            update_szig["remote_user"] = entity
            update_szig["remote_groups"] = str(groups)

        self.session.updateSzigConns(Z_SZIG_CONNECTION_PROPS, update_szig);


    def readPEM(self, filename):
        """<method internal="yes">
        </method>
        """
        proxyLog(self, CORE_DEBUG, 6, "Reading PEM file; filename='%s'" % filename)
        f = open(filename, 'r')
        res = f.read()
        f.close()
        return res

    def _hasMethod(self, obj, name):
        v = vars(obj.__class__)
        # check if name is defined directly in instance's class and
        # not in one of its ancestors and that name is a method
        return name in v and inspect.isroutine(v[name])
