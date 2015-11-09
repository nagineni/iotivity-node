{
	"variables": {
		"externalOCTBStack": '<!(if test "x${OCTBSTACK_CFLAGS}x" != "xx" -a "x${OCTBSTACK_CFLAGS}x" != "xx"; then echo true; else echo false; fi)',
	},

	"conditions": [

		# Build dlopennow when testing so we can make sure the library has all the symbols it needs
		[ "'<!(echo $TESTING)'=='true'", {
			"targets+": [
				{
					"target_name": "dlopennow",
					"sources": [ "tests/dlopennow.cc" ],
					"include_dirs": [
					"<!(node -e \"require('nan')\")"
					]
				}
			]
		} ]
	],

	"target_defaults": {
		"include_dirs": [
			"<!(node -e \"require('nan')\")"
		],
		"conditions": [

			# Platform-independent conditions

			[ "'<(externalOCTBStack)'=='true'", {
				"libraries": [ '<!@(echo "$OCTBSTACK_LIBS")' ],
				"cflags": [ '<!@(echo "$OCTBSTACK_CFLAGS")' ],
				"xcode_settings": {
					"OTHER_CFLAGS": [ '<!@(echo "$OCTBSTACK_CFLAGS")' ]
				}
			}, {
				"libraries": [
					'<!@(echo "-L$(pwd)/deps/iotivity/lib")',
					'-loctbstack',
					'<!@(echo "-Wl,-rpath $(pwd)/deps/iotivity/lib")'
				],
				"cflags": [
					'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/csdk/stack/include")',
					'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/csdk/ocrandom/include")',
					'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/c_common")',
					'-DROUTING_EP',
					'-DTCP_ADAPTER'
				],
				"xcode_settings": {
					"OTHER_CFLAGS": [
						'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/csdk/stack/include")',
						'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/csdk/ocrandom/include")',
						'<!@(echo "-I$(pwd)/deps/iotivity/include/iotivity/resource/c_common")',
						'-DROUTING_EP',
						'-DTCP_ADAPTER'
					]
				}
			} ],

			# OSX-specific conditions

			[ "OS=='mac' and '<(externalOCTBStack)'=='false'", {
				"libraries+": [
					"-lconnectivity_abstraction",
					"-lcoap",
					"-lc_common",
					"-lroutingmanager",
					"-locsrm"
				]
			} ],
			[ "OS=='mac'", {
				"xcode_settings": { "OTHER_CFLAGS": [ '-std=c++11' ] }
			} ]
		],
		"cflags_cc": [ '-std=c++11' ],
	},

	"targets": [
		{
			"target_name": "csdk",
			"type": "none",
			"conditions": [
				[ "'<(externalOCTBStack)'=='false'", {
					"actions": [ {
						"action_name": "build",
						"inputs": [""],
						"outputs": [""],
						"action": [
							"sh",
							"./build-csdk.sh",
							'<!@(if test "x${npm_config_debug}x" != "xtruex"; then echo ""; else echo "--debug"; fi)'
						],
						"message": "Building CSDK"
					} ]
				} ]
			]
		},
		{
			"target_name": "iotivity",
			"sources": [
				"src/constants.cc",
				"src/enums.cc",
				"src/functions.cc",
				"src/functions/oc-cancel.cc",
				"src/functions/oc-create-delete-resource.cc",
				"src/functions/oc-do-resource.cc",
				"src/functions/oc-do-response.cc",
				"src/functions/oc-notify.cc",
				"src/functions/oc-random.cc",
				"src/functions/oc-set-default-device-entity-handler.cc",
				"src/functions/simple.cc",
				"src/main.cc",
				"src/structures.cc",
				"src/structures/handles.cc",
				"src/structures/oc-client-response.cc",
				"src/structures/oc-dev-addr.cc",
				"src/structures/oc-entity-handler-response.cc",
				"src/structures/oc-header-option-array.cc",
				"src/structures/oc-payload.cc",
				"src/structures/oc-platform-info.cc",
				"src/structures/oc-sid.cc",
				"src/structures/string-primitive.cc"
			],
			"conditions": [
				[ "'<!(echo $TESTING)'=='true'", {
					"defines": [ "TESTING" ]
				} ]
			],
			"dependencies": [ "csdk" ]
		}
	]
}
