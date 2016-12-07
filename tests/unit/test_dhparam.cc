/***************************************************************************
 *
 * Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
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

#include <zorp/pyencryption_private.h>

#include <boost/test/unit_test.hpp>

BOOST_AUTO_TEST_CASE(test_valid_dhparams)
{
  const std::string dh_128(
    "-----BEGIN DH PARAMETERS-----\n"
    "MEYCQQD3HsPBqDnNxUxZVJleT47eUcLJ4X/B9llDa0YOON7nuy6MPFscC5JA82+G\n"
    "7/YTZMjaLWXJPqTXI7M0p/Qm1KKbAgEC\n"
    "-----END DH PARAMETERS-----\n"
  );
  BOOST_CHECK_NO_THROW(z_policy_encryption_get_dh_from_pem(dh_128.c_str(), dh_128.size()));

  const std::string dh_2048(
    "-----BEGIN DH PARAMETERS-----\n"
    "MIIBCAKCAQEAvCs7nmeWdIPItc2P23Ys2oLLhG0ipZHlmzzlnMz6Vz0dL+G5XY44\n"
    "x+SsUWmcqXAXFLxjJHfxOmc0B5e6yjPD2F4afUOl2O+zCyu6rUg1YQ+tAxpbVPqF\n"
    "xM7PXkSFO65sqRXihfP6ykkOxrPULIulm1LtmpFeEoH+URKELXwwW7clSDua4v0f\n"
    "/JW1lfPWHCKQYN5+lXrXmEH9tWhQBqg6r4ne52gVmLaxdGUNXIooXGXlewvycjzu\n"
    "jv/E+ULtuJ9rDAoDG9yXpERFd/Tvv8RBe2gdOi1p80G1XX3Ufebi0J6xsuOfaEUv\n"
    "jImxkdUPuXVeqkErk9Tah2bRkSm2w5mdswIBAg==\n"
    "-----END DH PARAMETERS-----\n"
  );
  BOOST_CHECK_NO_THROW(z_policy_encryption_get_dh_from_pem(dh_2048.c_str(), dh_2048.size()));
}

BOOST_AUTO_TEST_CASE(test_invalid_dhparams)
{
  const char *dh_null;
  BOOST_CHECK_THROW(z_policy_encryption_get_dh_from_pem(dh_null, 0),
                    std::invalid_argument);

  const std::string dh_empty;
  BOOST_CHECK_THROW(z_policy_encryption_get_dh_from_pem(dh_empty.c_str(), dh_empty.size()),
                    std::invalid_argument);

  const std::string dh_invalid(
    "-----BEGIN DH PARAMETERS-----\n"
    "-----END DH PARAMETERS-----\n"
  );
  BOOST_CHECK_THROW(z_policy_encryption_get_dh_from_pem(dh_invalid.c_str(), dh_invalid.size()),
                    std::invalid_argument);

}
