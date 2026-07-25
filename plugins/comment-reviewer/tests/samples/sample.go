// leading comment
package main

/* block
   comment */
func main() {
	url := "https://example.com//not-a-comment"
	raw := `back // tick`
	println(url, raw) // trailing
}
