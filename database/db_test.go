package database

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	"github.com/sweetrpg/common/logging"
	"github.com/sweetrpg/db/constants"
)

type DbTestSuite struct {
	suite.Suite
}

func (suite *DbTestSuite) SetupTest() {
	os.Unsetenv(constants.DB_URI)
	os.Unsetenv(constants.DB_NAME)
	os.Unsetenv(constants.DB_HOST)
	os.Unsetenv(constants.DB_SCHEME)
	os.Unsetenv(constants.DB_USER)
	os.Unsetenv(constants.DB_PW)
	os.Unsetenv(constants.DB_PORT)
	os.Unsetenv(constants.DB_OPTS)
}

func (suite *DbTestSuite) TestBuildURLFromURI() {
	os.Setenv(constants.DB_URI, "mongo://user:pass@host:12345/db?opts=these")
	dbUrl, dbName := buildDbURL()
	assert.Equal(suite.T(), dbUrl.Scheme, "mongo")
	assert.Equal(suite.T(), dbUrl.User.Username(), "user")
	// assert.Equal(t, dbUrl.User.Password(), "pass")
	assert.Equal(suite.T(), dbUrl.Host, "host:12345")
	assert.Equal(suite.T(), dbUrl.Query().Get("opts"), "these")
	assert.Equal(suite.T(), dbName, "db")
}

func (suite *DbTestSuite) TestBuildURLFromParts() {
	os.Setenv(constants.DB_NAME, "db")
	os.Setenv(constants.DB_HOST, "host")
	os.Setenv(constants.DB_SCHEME, "mongo")
	os.Setenv(constants.DB_USER, "user")
	os.Setenv(constants.DB_PW, "pass")
	os.Setenv(constants.DB_PORT, "12345")
	os.Setenv(constants.DB_OPTS, "opts=these")

	dbUrl, dbName := buildDbURL()
	assert.Equal(suite.T(), dbUrl.Scheme, "mongo")
	assert.Equal(suite.T(), dbUrl.User.Username(), "user")
	// assert.Equal(t, dbUrl.User.Password(), "pass")
	assert.Equal(suite.T(), dbUrl.Host, "host:12345")
	assert.Equal(suite.T(), dbUrl.Query().Get("opts"), "these")
	assert.Equal(suite.T(), dbName, "db")
}

func (suite *DbTestSuite) TestInvalidURL() {
	os.Setenv(constants.DB_URI, "bogus!this is some b4d URI^#$%")

	assert.Panics(suite.T(), func() { buildDbURL() }, "Should have panicked")
}

func (suite *DbTestSuite) TestGet() {
	logging.Init()

	SetupDatabase()

	type DBObject struct {
		Key   string `bson:"key"`
		Value string `bson:"value"`
	}

	object, err := Get[DBObject](os.Getenv("TEST_COLLECTION"), os.Getenv("TEST_ID"))
	assert.NotNil(suite.T(), object)
	assert.Nil(suite.T(), err)
}

func TestDbTestSuite(t *testing.T) {
	suite.Run(t, new(DbTestSuite))
}
