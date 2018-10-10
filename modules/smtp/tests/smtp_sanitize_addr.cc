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
 ***************************************************************************/

#define BOOST_TEST_MAIN
#include <boost/test/unit_test.hpp>

#include "../smtp.h"

SmtpProxy *dummy;

int exit_code = 0;

#define SAFE_STR(x)  ((x) ? x : "(NULL)")

void
test_case(gchar *path, gchar *email, gboolean expected)
{
  GString *result = g_string_sized_new(128);
  gchar *end = 0;

  BOOST_CHECK_MESSAGE(smtp_sanitize_address(dummy, result, path, TRUE, &end) == expected, "failure, different parsing, path=" << path << ", email=" << email << ", result=" << result->str << ", end=" << end);
  BOOST_CHECK_MESSAGE(expected && (strcmp(result->str, email) == 0) || !expected, "failure, different email, path=" << path <<", email=" << email << ", end=" << end);
}

BOOST_AUTO_TEST_CASE(test_sanitize_addr)
{
  dummy = (SmtpProxy *) z_object_new(Z_CLASS(SmtpProxy));
  dummy->append_domain = g_string_sized_new(0);
  /* z_charset_parse(&dummy.local_part, "a-zA-Z0-9\\-=._"); */
  test_case("<username@domain>", "username@domain", TRUE);
  test_case("<>", "", TRUE);
  test_case("<@hop1,@hop2,@hop3:username@domain>", "username@domain", TRUE);
  test_case("<@:username@domain>", NULL, FALSE);
  test_case("<:username@domain>", NULL, FALSE);
  test_case("<@hop1@username@domain>", NULL, FALSE);
  test_case("<@hop1\"username@domain>", NULL, FALSE);
  test_case("<@hop1:;username@domain>", NULL, FALSE);
  test_case("<@hop1,username@domain>", NULL, FALSE);
  test_case("<username@domain", NULL, FALSE);
  test_case("username@domain>", NULL, FALSE);
  test_case("username@domain", NULL, FALSE);
  test_case("<usernamedomain>", NULL, FALSE);
  test_case("<\"firstname lastname\"@domain>", "\"firstname lastname\"@domain", TRUE);
  test_case("<\"firstname lastname\"@[1.2.3.4]>", "\"firstname lastname\"@[1.2.3.4]", TRUE);
  test_case("<@hop1.domain,@hop2.domain:\"firstname lastname\"@[1.2.3.4]>", "\"firstname lastname\"@[1.2.3.4]", TRUE);
  test_case("<@hop1.domain,@hop2.domain:\"firstname lastname\"@[domain literal]>", "\"firstname lastname\"@[domain literal]", TRUE);
  test_case("<@hop1.domain,@hop2.domain:\"firstname lastname\"@#123456>", "\"firstname lastname\"@#123456", TRUE);
  test_case("<@hop1.domain,@hop2.domain:\"firstname lastname\"@#123456z>", NULL, FALSE);
  test_case("<bounce-debian-gcc=asd=domain@lists.debian.org> SIZE=10037", "bounce-debian-gcc=asd=domain@lists.debian.org", TRUE);
  test_case("username@domain", NULL, FALSE);
  test_case("<username@domain", NULL, FALSE);
  test_case("username@domain>", NULL, FALSE);
  dummy->permit_omission_of_angle_brackets = TRUE;
  printf("------\n");
  test_case("username@domain", "username@domain", TRUE);
  test_case("<username@domain>", "username@domain", TRUE);
  test_case("<username@domain", "username@domain", FALSE);
  test_case("username@domain>", "username@domain", FALSE);
  test_case("bounce-debian-gcc=asd=domain@lists.debian.org SIZE=10037", "bounce-debian-gcc=asd=domain@lists.debian.org", TRUE);
}
