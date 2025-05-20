% if license_str is not None:
% for line in license_str.strip().split('\n'):
// ${line}
% endfor

%endif
#ifndef ${top_name.upper() + "_H"}
#define ${top_name.upper() + "_H"}

% for blk in blocks:
    % for entry in blk:
#define ${entry["name"]} ${"0x{num:08X}".format(num = entry["num"])}
    % endfor

% endfor

% for enum in enums:
    % for field in enum["choices"]:
#define ${enum["name"]}__${field["name"]} ${field["value"]}
    % endfor

% endfor

#endif /* ${top_name.upper() + "_H"} */
