package config

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
}

func GetDatabaseConfig() *DatabaseConfig {
	return &DatabaseConfig{
		Host:     "localhost",
		Port:     3306,
		User:     "root",
		Password: "your_password",
		DBName:   "trading_db",
	}
}
