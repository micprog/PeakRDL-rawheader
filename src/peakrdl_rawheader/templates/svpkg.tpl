% if license_str is not None:
% for line in license_str.strip().split('\n'):
// ${line}
% endfor

%endif
package ${top_name + "_addrmap_pkg"};

% for blk in blocks:
    % for entry in blk:
localparam longint unsigned ${entry["name"]} = ${"64'h{num:08X}".format(num = entry["num"])};
    % endfor

% endfor

endpackage;
