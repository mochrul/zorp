/***************************************************************************
 *
 * Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
 * Copyright (c) 2015-2018 BalaSys IT Ltd, Budapest, Hungary
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 *
 ***************************************************************************/

#include <zorp/zorp.h>
#include <zorpll/socket.h>
#include <zorp/tpsocket.h>
#include <zorpll/log.h>
#include <zorpll/cap.h>

#include <string.h>
#include <stdlib.h>

#include <netinet/in.h>

static gint
z_do_ll_getdestname(gint fd, struct sockaddr *sa, socklen_t *salen, guint32 sock_flags G_GNUC_UNUSED)
{
  return getsockname(fd, sa, salen);
}

static gint
z_do_tp40_bind(gint fd, struct sockaddr *sa, socklen_t salen, guint32 sock_flags)
{
  gint on = 1, res;

  z_enter();
  if (sock_flags & ZSF_TRANSPARENT || sock_flags & ZSF_MARK_TPROXY)
    {
#if defined(__gnu_linux__)
#if HAVE_DECL_IP_TRANSPARENT
      if (setsockopt(fd, IPPROTO_IP, IP_TRANSPARENT, &on, sizeof(on)) < 0)
        z_return(false);
#endif
#if HAVE_DECL_IP_FREEBIND
      if (setsockopt(fd, IPPROTO_IP, IP_FREEBIND, &on, sizeof(on)) < 0)
        z_return(false);
#endif
#elif defined(__FreeBSD__)
#if HAVE_DECL_IP_BINDANY
      if (setsockopt(fd, IPPROTO_IP, IP_BINDANY, &on, sizeof(on)) < 0)
        z_return(false);
#endif
#endif
    }
  res = z_do_ll_bind(fd, sa, salen, sock_flags);
  z_return(res);
}

static ZSocketFuncs z_tp40_socket_funcs =
{
  z_do_tp40_bind,
  z_do_ll_accept,
  z_do_ll_connect,
  z_do_ll_listen,
  z_do_ll_getsockname,
  z_do_ll_getpeername,
  z_do_ll_getdestname
};

gboolean
z_tp_socket_init(void)
{
  socket_funcs = &z_tp40_socket_funcs;
  return TRUE;
}
