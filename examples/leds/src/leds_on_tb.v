//-------------------------------------------------------------------
//-- leds_on_tb.v
//-- Testbench
//-------------------------------------------------------------------
//-- March 2016. Written by Juan Gonzalez (Obijuan) and Jesus Arroyo
//-------------------------------------------------------------------
`default_nettype none
`timescale 100 ns / 10 ns
`define DUMPSTR(x) `"x.vcd`"


module leds_on_tb();

//-- Simulation time: 1us (10 * 100ns)
parameter DURATION = 10;

//-- Clock signal. It is not used in this simulation
reg clk = 0;
always #0.5 clk = ~clk;

//-- Leds port
wire [7:0] lport;

//-- Instantiate the unit to test
leds_on UUT (.LPORT(lport));

initial begin
  //-- File were to store the simulation results
  $dumpfile(`DUMPSTR(`VCD_OUTPUT));
  $dumpvars(0, leds_on_tb);

   #(DURATION) $display("End of simulation");
  $finish;
end

endmodule
