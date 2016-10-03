//-------------------------------------------------------------------
//-- counter_tb.v
//-- Testbench
//-------------------------------------------------------------------
//-- March 2016. Written by Juan Gonzalez (Obijuan) and Jesus Arroyo
//-------------------------------------------------------------------

`default_nettype none
`timescale 100 ns / 10 ns
`define DUMPSTR(x) `"x.vcd`"


module counter_tb();

//-- Simulation time: 1us (10 * 100ns)
parameter DURATION = 10;

//-- Clock signal. It is not used in this simulation
reg clk = 0;
always #0.5 clk = ~clk;

//-- Leds port
wire [4:0] leds;

//-- Counter bits length
localparam N = 6;

counter #(
           .N(N)
)  CONT0 (
           .clk(clk),
           .leds(leds)
);

initial begin
  //-- File where to store the simulation
  $dumpfile(`DUMPSTR(`VCD_OUTPUT));
  $dumpvars(0, counter_tb);

  #(DURATION) $display("END of the simulation");
  $finish;
end

endmodule
