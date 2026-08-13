import { Link } from 'react-router-dom'

import React from 'react'

function NotFoundPage() {
  return (
    <>
      <div>404 Not Found</div>
      {/* using link is technically an a tag but wont refresh the page */}
      <Link to = "/">Return To Home</Link>
    </>
  )
}

export default NotFoundPage