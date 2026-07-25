// real comment, unrelated to the JSDoc block below

/**
 * Validates a user-supplied email address.
 * @param {string} email - the address to validate
 * @returns {boolean} true when the address is well-formed
 */
function validate(email) {
  return /.+@.+/.test(email);
}
