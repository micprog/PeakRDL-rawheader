% if license_str is not None:
% for line in license_str.strip().split('\n'):
// ${line}
% endfor

%endif
`ifndef ${top_name.upper() + "_SVH"}
`define ${top_name.upper() + "_SVH"}

% for blk in blocks:
    % for entry in blk:
`define ${entry["name"]} ${"64'h{num:08X}".format(num = entry["num"])}
    % endfor

% endfor

`endif /* ${top_name.upper() + "_SVH"} */
