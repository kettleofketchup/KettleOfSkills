// leading comment
/* outer /* inner */ still outer */
fn main() {
    let s = "slash // inside";
    println!("{} don't", s); // trailing
}
