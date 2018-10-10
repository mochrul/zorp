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

#include "../http.h"

#define TEST_ID "id=" << id << ", "

void
test_case(
  gint id,
  gchar *cookie_value_in_str,
  gint cookie_count,
  gchar *cookie_name_str,
  gboolean cookie_exists_in_input,
  gboolean cookie_header_still_present,
  gchar *cookie_value_out_str)
{
  HttpHeaders hdrs;

  http_init_headers(&hdrs);

  HttpHeader *cookie_hdr = http_add_header(&hdrs, "Cookie", strlen("Cookie"),
                                           cookie_value_in_str, strlen(cookie_value_in_str));

  BOOST_REQUIRE_MESSAGE(cookie_hdr != NULL, TEST_ID "header is NULL");

  CookiePairVector cookie_vector = http_parse_header_cookie(&hdrs);

  BOOST_REQUIRE_MESSAGE(cookie_vector.size() == cookie_count, TEST_ID "parsed cookies count"
                        "does not match: " << cookie_vector.size() << "' != '" << cookie_count);

  // for (auto &cookie_pair: cookie_vector)
  //   BOOST_TEST_MESSAGE("- '" << cookie_pair.first.c_str() << "': '" << cookie_pair.second.c_str()) << "'";

  CookiePairVector::iterator it = http_find_cookie_by_name(cookie_vector, cookie_name_str);
  if (cookie_exists_in_input)
    {
      if (it == cookie_vector.end())
        BOOST_FAIL(TEST_ID "could not find element to be deleted");
      else
        cookie_vector.erase(it);
    }

  http_write_header_cookie(&hdrs, cookie_vector);

  BOOST_REQUIRE_MESSAGE(cookie_hdr->present == cookie_header_still_present, TEST_ID "presents are not equal");

  BOOST_REQUIRE_MESSAGE(strcmp(cookie_hdr->value->str, cookie_value_out_str) == 0,
      TEST_ID "cookie values are not equal: '"
      << cookie_hdr->value->str << "' != '"<< cookie_value_out_str << "'");

  http_destroy_headers(&hdrs);
}

struct
{
  gchar *cookie_value_in_str;
  gint cookie_count;
  gchar *cookie_name_str;
  gboolean cookie_exists_in_input;
  gboolean cookie_header_still_present;
  gchar *cookie_value_out_str;
} test_table[] =
{
  { "",                   0, "a", FALSE, FALSE, ""              },
  { "c=d",                1, "a", FALSE, TRUE,  "c=d"           },
  { "a=b",                1, "a", TRUE,  FALSE, ""              },
  { "c=d; a=b",           2, "a", TRUE,  TRUE,  "c=d"           },
  { "a=; c=d",            2, "a", TRUE,  TRUE,  "c=d"           },
  { "c=d; a=",            2, "a", TRUE,  TRUE,  "c=d"           },
  { "c=y; a=b; e=f",      3, "a", TRUE,  TRUE,  "c=y; e=f"      },
  { "c=y; a=; e=f",       3, "a", TRUE,  TRUE,  "c=y; e=f"      },
  { "c=y; a=b; j=; e=f",  4, "a", TRUE,  TRUE,  "c=y; j=; e=f"  },
  { "c=1; a=b; c=2; c=3", 4, "a", TRUE,  TRUE,  "c=1; c=2; c=3" },
  // against RFC6265 cases
  { "a=;c=d",             1, "a", TRUE,  FALSE, ""              },
  { "c=x a=b",            1, "a", FALSE, TRUE,  "c=x a=b"       },
  { "c=d;a=b",            1, "a", FALSE, TRUE,  "c=d;a=b"       },
  { "c=z; a=b;",          2, "a", TRUE,  TRUE,  "c=z"           },
  { "a=b; c=z;",          2, "a", TRUE,  TRUE,  "c=z;"          },
  { "c=d; a=b ",          2, "a", TRUE,  TRUE,  "c=d"           },
  // google cookies :D
  { "SID=vwR1mC_SYYQ1WK33GWzEGLFlKXwJDSVp_ck4MjRkysk_da5EDKPRmRVNNV9RV-xYg.; "
    "HSID=Axlp7hps4uEFjrx; "
    "SSID=A7H6eDQBq182KBJ; "
    "APISID=qf1JXJwX_V-jh-f/AKQdAhX9GH40pTat; "
    "SAPISID=7E60KATkB_7SHg/Az6JTF6jJbz3hDf; "
    "CONSENT=YES+CZ.hu+V7; "
    "NID=110=SW1vfQD39EcrcRPJDf7eYNCiXU64zsFYmphqzfX25teL6IanS07PMyPG1NFwfxrtz6yP97TuEkGSPGBjlfm_6wSsfw-AcOi_7BdRqk"
    "sHcrDN3i4eKJGNE2AAZvph3rWxJUg7N1wnS-ft_1e3WNPg_lFEqJuejdzQ4GuvFAHX8TnXhVYFLoXCMP3WZKr_DLUoYTuWmR1j5ikP-1HRqH; "
    "ga=GA1.3.151932345.1491309292; "
    "gid=GA1.3.1394511831.1502964263",
                     9, "APISID", TRUE,  TRUE,
    "SID=vwR1mC_SYYQ1WK33GWzEGLFlKXwJDSVp_ck4MjRkysk_da5EDKPRmRVNNV9RV-xYg.; "
    "HSID=Axlp7hps4uEFjrx; "
    "SSID=A7H6eDQBq182KBJ; "
    "SAPISID=7E60KATkB_7SHg/Az6JTF6jJbz3hDf; "
    "CONSENT=YES+CZ.hu+V7; "
    "NID=110=SW1vfQD39EcrcRPJDf7eYNCiXU64zsFYmphqzfX25teL6IanS07PMyPG1NFwfxrtz6yP97TuEkGSPGBjlfm_6wSsfw-AcOi_7BdRqk"
    "sHcrDN3i4eKJGNE2AAZvph3rWxJUg7N1wnS-ft_1e3WNPg_lFEqJuejdzQ4GuvFAHX8TnXhVYFLoXCMP3WZKr_DLUoYTuWmR1j5ikP-1HRqH; "
    "ga=GA1.3.151932345.1491309292; "
    "gid=GA1.3.1394511831.1502964263",},
  { NULL, 0, NULL, FALSE, FALSE, NULL }
};

BOOST_AUTO_TEST_CASE(test_remove_cookie)
{
  //// for (unoptimized!) performance and memory leak testing
  //// 0.1 million test run takes 5 second
  //gint j;
  //for (j = 0; j < 100000; j++)
  //  {
  gint i;
  for (i = 0; test_table[i].cookie_value_in_str; i++)
    {
      test_case(i, test_table[i].cookie_value_in_str, test_table[i].cookie_count, test_table[i].cookie_name_str,
                test_table[i].cookie_exists_in_input, test_table[i].cookie_header_still_present,
                test_table[i].cookie_value_out_str);
    }
  //  }
}
