#!/bin/bash

# Update enums in src/enums.cc. This file uses pkgconfig to determine the location of octypes.h and
# ocstackconfig.h, but only if the environment variable OCTBSTACK_CFLAGS is unset.
#
# src/enums.cc contains the comment "// The rest of this file is generated". This script preserves
# the file up to and including the comment, and discards the rest of the file. It then appends to
# src/enums.cc the enum definitions from octypes.h
#
# The script also generates the function InitEnums() which the file is expected to export.

if test "x${OCTBSTACK_CFLAGS}x" = "xx"; then
	export OCTBSTACK_CFLAGS=$( pkg-config --cflags octbstack )
fi

. ./constants-and-enums.common.sh

# enums.cc

# Copy the boilerplate from the existing file
awk -v PRINT=1 '{
	if ( PRINT ) print;
	if ( $0 == "// The rest of this file is generated" ) {
		PRINT=0;
		print( "" );
	}
}' \
< src/enums.cc > src/enums.cc.new || ( rm -f src/enums.cc.new && exit 1 )

# Parse header for enums
cat "${OCTYPES_H}" "${OCRANDOM_H}" "${OCPRESENCE_H}" | \
  grep -vE '#(ifdef|define|endif)|^\s*/' | \
  grep -v '^$' | \
  awk -v PRINT=0 -v OUTPUT="" -v ENUM_LIST="" '{
    if ( $0 == "typedef enum" ) PRINT=1;
    if ( PRINT == 1 ) {
      if ( !( $1 ~ /^[{}]/ ) && $1 != "typedef" ) {
	    if ( $1 ~ /^[A-Z]/ ) {
          OUTPUT = OUTPUT "  SET_CONSTANT_NUMBER(returnValue, " $1 ");\n";
        }
      } else if ( $1 ~ /^}/ ) {
	    ENUM_NAME = $0;
	    gsub( /^} */, "", ENUM_NAME );
	    gsub( / *;.*$/, "", ENUM_NAME );
        ENUM_LIST = ENUM_LIST "  SET_ENUM(exports, " ENUM_NAME ");\n";
        print("static Local<Object> bind_" ENUM_NAME "() {\n  Local<Object> returnValue = Nan::New<Object>();\n" );
      }
      else if ( $1 != "typedef" && $1 != "{" ) {
        print;
      }
      if ( $0 ~ /;$/ ) {
        PRINT=0;
        print( OUTPUT "\n  return returnValue;\n}\n" );
        OUTPUT="";
      }
    }
  }
  END {
    print( "void InitEnums(Handle<Object> exports) {\n" ENUM_LIST "}" );
  }' | \
  sed 's/[,=]);$/);/' >> src/enums.cc.new || ( rm -f src/enums.cc.new && exit 1 )

# Replace the original file with the generated file
mv -f src/enums.cc.new src/enums.cc || ( rm -f src/enums.cc.new && exit 1 )
