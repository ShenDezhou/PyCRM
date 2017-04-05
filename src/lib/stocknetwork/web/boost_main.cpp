#define BOOST_ALL_DYN_LINK
#define BOOST_AUTO_TEST_MAIN
#include <boost/test/auto_unit_test.hpp>
#include "main.cpp"


BOOST_AUTO_TEST_CASE(test_create_final)
{
  printf("hello");
  BOOST_CHECK( 0 );
  BOOST_REQUIRE( 0 );
  BOOST_ERROR("hhhh");
  BOOST_FAIL("mmm");
  BOOST_CHECK_MESSAGE(getMimeType(const_cast<char*>("abc.html")) == "text/txt", "not working...");
  BOOST_CHECK_EQUAL(1,2);
  printf("over.");
}
